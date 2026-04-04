import faiss
import numpy as np
import pandas as pd
import pickle
import os
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict, Any


class FAISSCreditIndex:
    def __init__(self):
        self.index = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.training_data = None
        self.labels = None
        self.index_trained = False

    def build_index(self, X_train: pd.DataFrame, y_train: pd.Series, nlist: int = 100, m: int = None, nbits: int = 8) -> None:
        self.feature_names = X_train.columns.tolist()
        median_vals = X_train.median()
        X_clean = X_train.fillna(median_vals).replace([np.inf, -np.inf], np.nan).fillna(median_vals)
        self.labels = y_train.values
        X_scaled = self.scaler.fit_transform(X_clean)
        self.training_data = X_scaled.astype('float32')
        d = X_scaled.shape[1]
        if m is None:
            divisors = [i for i in range(1, d + 1) if d % i == 0]
            for candidate in [2, 4, 5, 8, 10]:
                if candidate in divisors:
                    m = candidate
                    break
            if m is None:
                m = divisors[1] if len(divisors) > 1 else 1
        if d % m != 0:
            divisors = [i for i in range(1, d + 1) if d % i == 0]
            m = min(divisors, key=lambda x: abs(x - m))
        print(f"Building FAISS IVF-PQ index: d={d}, m={m}, nlist={nlist}, nbits={nbits}")
        quantizer = faiss.IndexFlatL2(d)
        self.index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)
        self.index.train(self.training_data)
        self.index.add(self.training_data)
        self.index_trained = True
        print(f"FAISS index built: {self.index.ntotal} vectors, {nlist} clusters")

    def search_similar(self, query: np.ndarray, k: int = 10, nprobe: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        if self.index is None:
            raise ValueError("Index not built. Call build_index first.")
        self.index.nprobe = nprobe
        if query.ndim == 1:
            query = query.reshape(1, -1)
        query_scaled = self.scaler.transform(query).astype('float32')
        return self.index.search(query_scaled, k)

    def find_similar_applicants(self, applicant_data: pd.DataFrame, k: int = 10) -> Dict[str, Any]:
        distances, indices = self.search_similar(applicant_data.values, k=k)
        similar_labels = self.labels[indices[0]]
        default_count = int(similar_labels.sum())
        default_rate = default_count / len(similar_labels)
        return {"similar_indices": indices[0].tolist(), "distances": distances[0].tolist(), "default_labels": similar_labels.tolist(), "default_count": default_count, "total_similar": len(similar_labels), "default_rate": float(default_rate), "risk_assessment": "high" if default_rate > 0.3 else "medium" if default_rate > 0.1 else "low"}

    def explain_denial_with_similar_approved(self, applicant_data: pd.DataFrame, shap_values: np.ndarray, feature_names: List[str], k: int = 20, min_approved: int = 5) -> Dict[str, Any]:
        distances, indices = self.search_similar(applicant_data.values, k=k)
        similar_labels = self.labels[indices[0]]
        approved_mask = similar_labels == 0
        approved_indices = indices[0][approved_mask]
        approved_distances = distances[0][approved_mask]
        shap_vals = shap_values.flatten() if shap_values.ndim > 1 else shap_values
        top_risk_idx = np.argsort(np.abs(shap_vals))[::-1][:5]
        top_risk_factors = [{"feature": feature_names[i], "shap_value": float(shap_vals[i]), "direction": "increases_risk" if shap_vals[i] > 0 else "decreases_risk"} for i in top_risk_idx]
        counter_examples = [{"index": int(idx), "distance": float(dist), "approved": True} for idx, dist in zip(approved_indices[:min_approved], approved_distances[:min_approved])]
        return {"denied": True, "top_risk_factors": top_risk_factors, "similar_approved_count": int(approved_mask.sum()), "counter_examples": counter_examples, "explanation": f"Found {int(approved_mask.sum())} similar applicants approved. Key risk: {', '.join([f['feature'] for f in top_risk_factors[:3]])}"}

    def get_neighbor_features(self, applicant_data: pd.DataFrame, k: int = 5) -> Dict[str, Any]:
        distances, indices = self.search_similar(applicant_data.values, k=k)
        similar_labels = self.labels[indices[0]]
        similar_distances = distances[0]
        weights = 1.0 / (similar_distances + 1e-6)
        weights = weights / weights.sum()
        weighted_risk = float(np.dot(similar_labels, weights))
        return {"neighbor_default_rate": float(similar_labels.mean()), "avg_neighbor_distance": float(similar_distances.mean()), "min_neighbor_distance": float(similar_distances.min()), "weighted_neighbor_risk": weighted_risk, "neighbor_count": k, "features": {"faiss_neighbor_default_rate": float(similar_labels.mean()), "faiss_avg_distance": float(similar_distances.mean()), "faiss_weighted_risk": weighted_risk}}

    def compute_cluster_centroids(self, n_clusters: int = 10) -> np.ndarray:
        if self.training_data is None:
            raise ValueError("No training data available.")
        kmeans = faiss.Kmeans(self.training_data.shape[1], n_clusters, niter=20, verbose=False)
        kmeans.train(self.training_data)
        return kmeans.centroids

    def monitor_drift(self, new_data: pd.DataFrame, n_clusters: int = 10) -> Dict[str, Any]:
        train_centroids = self.compute_cluster_centroids(n_clusters)
        new_scaled = self.scaler.transform(new_data.values).astype('float32')
        kmeans_new = faiss.Kmeans(new_scaled.shape[1], n_clusters, niter=20, verbose=False)
        kmeans_new.train(new_scaled)
        new_centroids = kmeans_new.centroids
        centroid_distances = np.linalg.norm(train_centroids - new_centroids, axis=1)
        index_temp = faiss.IndexFlatL2(train_centroids.shape[1])
        index_temp.add(train_centroids.astype('float32'))
        _, cluster_assignments = index_temp.search(new_scaled, 1)
        train_cluster_dist = np.zeros(n_clusters)
        new_cluster_dist = np.zeros(n_clusters)
        _, train_clusters = index_temp.search(self.training_data, 1)
        for c in train_clusters.flatten():
            train_cluster_dist[int(c)] += 1
        train_cluster_dist = train_cluster_dist / train_cluster_dist.sum()
        for c in cluster_assignments.flatten():
            new_cluster_dist[int(c)] += 1
        new_cluster_dist = new_cluster_dist / new_cluster_dist.sum()
        kl_div = float(np.sum(train_cluster_dist * np.log((train_cluster_dist + 1e-10) / (new_cluster_dist + 1e-10))))
        return {"avg_centroid_distance": float(centroid_distances.mean()), "max_centroid_distance": float(centroid_distances.max()), "kl_divergence": kl_div, "drift_detected": kl_div > 0.1 or float(centroid_distances.mean()) > 1.0, "drift_level": "high" if kl_div > 0.2 else "medium" if kl_div > 0.1 else "low", "train_distribution": train_cluster_dist.tolist(), "new_distribution": new_cluster_dist.tolist()}

    def cluster_customers(self, data: pd.DataFrame, n_clusters: int = 5) -> Dict[str, Any]:
        data_scaled = self.scaler.transform(data.values).astype('float32')
        kmeans = faiss.Kmeans(data_scaled.shape[1], n_clusters, niter=20, verbose=False)
        kmeans.train(data_scaled)
        _, cluster_assignments = kmeans.index.search(data_scaled, 1)
        cluster_assignments = cluster_assignments.flatten()
        clusters_info = []
        for cluster_id in range(n_clusters):
            mask = cluster_assignments == cluster_id
            cluster_size = int(mask.sum())
            if cluster_size > 0:
                cluster_default_rate = float(self.labels[mask].mean()) if self.labels is not None and len(self.labels) == len(data) else None
                centroid_unscaled = self.scaler.inverse_transform(kmeans.centroids[cluster_id].reshape(1, -1)).flatten()
                clusters_info.append({"cluster_id": cluster_id, "size": cluster_size, "percentage": float(cluster_size / len(data) * 100), "default_rate": cluster_default_rate, "centroid": {name: float(val) for name, val in zip(self.feature_names, centroid_unscaled)} if self.feature_names else {}})
        clusters_info.sort(key=lambda x: x["default_rate"] or 0, reverse=True)
        return {"n_clusters": n_clusters, "total_customers": len(data), "clusters": clusters_info, "cluster_labels": cluster_assignments.tolist()}

    def save_index(self, save_dir: str = 'saved_models') -> None:
        os.makedirs(save_dir, exist_ok=True)
        faiss.write_index(self.index, os.path.join(save_dir, 'faiss_index.index'))
        with open(os.path.join(save_dir, 'faiss_meta.pkl'), 'wb') as f:
            pickle.dump({'scaler': self.scaler, 'feature_names': self.feature_names, 'labels': self.labels, 'training_data': self.training_data}, f)
        print(f"FAISS index saved to {save_dir}")

    def load_index(self, save_dir: str = 'saved_models') -> 'FAISSCreditIndex':
        self.index = faiss.read_index(os.path.join(save_dir, 'faiss_index.index'))
        with open(os.path.join(save_dir, 'faiss_meta.pkl'), 'rb') as f:
            meta = pickle.load(f)
            self.scaler = meta['scaler']
            self.feature_names = meta['feature_names']
            self.labels = meta['labels']
            self.training_data = meta['training_data']
        self.index_trained = True
        print("FAISS index loaded successfully")
        return self


def build_and_save_faiss_index(data_path: str = 'data/cs-training.csv', save_dir: str = 'saved_models') -> FAISSCreditIndex:
    df = pd.read_csv(data_path)
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)
    X = df.drop(['SeriousDlqin2yrs'], axis=1)
    y = df['SeriousDlqin2yrs']
    faiss_index = FAISSCreditIndex()
    faiss_index.build_index(X, y)
    faiss_index.save_index(save_dir)
    return faiss_index


if __name__ == "__main__":
    build_and_save_faiss_index()