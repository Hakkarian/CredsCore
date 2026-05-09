"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { socialCapitalApi, NetworkData, NetworkNode, NetworkEdge } from "@/lib/api";
import { cn } from "@/lib/utils";
import styles from "./NetworkGraph.module.scss";

interface NetworkGraphProps {
  applicantId: string;
}

interface PositionedNode extends NetworkNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export function NetworkGraph({ applicantId }: NetworkGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(0);
  const nodesRef = useRef<PositionedNode[]>([]);
  const edgesRef = useRef<NetworkEdge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"organic" | "radial" | "hierarchical">("organic");
  const [hoveredNode, setHoveredNode] = useState<PositionedNode | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const WIDTH = 600;
  const HEIGHT = 300;
  const CENTER_X = WIDTH / 2;
  const CENTER_Y = HEIGHT / 2;

  // Fetch network data
  useEffect(() => {
    async function fetchNetwork() {
      try {
        setLoading(true);
        const data = await socialCapitalApi.getVisualizationData(applicantId, 2);

        // Initialize positions based on view mode
        const nodes: PositionedNode[] = data.nodes.map((node, i) => {
          let x = CENTER_X;
          let y = CENTER_Y;

          if (node.id === data.entity_id) {
            x = CENTER_X;
            y = CENTER_Y;
          } else {
            const angle = (i / data.nodes.length) * 2 * Math.PI;
            const radius = 80 + Math.random() * 60;
            x = CENTER_X + Math.cos(angle) * radius;
            y = CENTER_Y + Math.sin(angle) * radius;
          }

          return { ...node, x, y, vx: 0, vy: 0 };
        });

        nodesRef.current = nodes;
        edgesRef.current = data.edges;
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load network");
        setLoading(false);
      }
    }

    fetchNetwork();
  }, [applicantId]);

  // Update positions when view mode changes
  useEffect(() => {
    const nodes = nodesRef.current;
    if (!nodes.length) return;

    const updated = nodes.map((node, i) => {
      if (node.id === edgesRef.current[0]?.source) {
        return { ...node, x: CENTER_X, y: CENTER_Y, vx: 0, vy: 0 };
      }

      let x, y;
      switch (viewMode) {
        case "radial": {
          const angle = (i / nodes.length) * 2 * Math.PI;
          const radius = 80 + (i % 3) * 30;
          x = CENTER_X + Math.cos(angle) * radius;
          y = CENTER_Y + Math.sin(angle) * radius;
          break;
        }
        case "hierarchical": {
          const level = Math.min(Math.floor(i / 4), 3);
          const offset = (i % 4) - 1.5;
          x = CENTER_X + offset * 60;
          y = CENTER_Y - 100 + level * 70;
          break;
        }
        default: {
          const angle = (i / nodes.length) * 2 * Math.PI;
          const radius = 60 + Math.random() * 80;
          x = CENTER_X + Math.cos(angle) * radius;
          y = CENTER_Y + Math.sin(angle) * radius;
        }
      }

      return { ...node, x, y, vx: 0, vy: 0 };
    });

    nodesRef.current = updated;
  }, [viewMode]);

  // Canvas rendering
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, WIDTH, HEIGHT);

    // Draw edges
    ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
    ctx.lineWidth = 1;
    edgesRef.current.forEach((edge) => {
      const source = nodesRef.current.find((n) => n.id === edge.source);
      const target = nodesRef.current.find((n) => n.id === edge.target);
      if (source && target) {
        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.stroke();
      }
    });

    // Draw nodes
    nodesRef.current.forEach((node) => {
      const isCenter = node.id === edgesRef.current[0]?.source;
      const radius = isCenter ? 12 : 6;

      // Node color based on type
      let color = "#F3CA40"; // default
      if (node.type === "individual") color = "#F3CA40";
      else if (node.type === "organization") color = "#22d3ee";
      else if (node.type === "business") color = "#a78bfa";

      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();

      if (isCenter) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius + 3, 0, 2 * Math.PI);
        ctx.strokeStyle = "rgba(243, 202, 64, 0.3)";
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });

    // Draw tooltip for hovered node
    if (hoveredNode) {
      const tooltipX = hoveredNode.x + 15;
      const tooltipY = hoveredNode.y - 10;

      ctx.fillStyle = "rgba(0, 0, 0, 0.85)";
      ctx.fillRect(tooltipX, tooltipY, 120, 40);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.2)";
      ctx.strokeRect(tooltipX, tooltipY, 120, 40);

      ctx.fillStyle = "#ffffff";
      ctx.font = "11px Inter, system-ui";
      ctx.fillText(hoveredNode.label, tooltipX + 8, tooltipY + 16);
      ctx.fillStyle = "#a3a3a3";
      ctx.fillText(hoveredNode.type, tooltipX + 8, tooltipY + 30);
    }
  }, [hoveredNode]);

  // Animation loop
  useEffect(() => {
    if (loading || error) return;

    function animate() {
      draw();
      animationRef.current = requestAnimationFrame(animate);
    }

    animate();
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [loading, error, draw]);

  // Mouse interaction
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left) * (WIDTH / rect.width);
    const y = (e.clientY - rect.top) * (HEIGHT / rect.height);

    setMousePos({ x, y });

    const hovered = nodesRef.current.find(
      (node) => Math.sqrt((node.x - x) ** 2 + (node.y - y) ** 2) < 15
    );
    setHoveredNode(hovered || null);
  }, []);

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <svg className={styles.loadingSpinner} viewBox="0 0 24 24" fill="none">
          <circle className={styles.spinnerCircle} cx="12" cy="12" r="10" stroke="#F3CA40" strokeWidth="4" />
          <path className={styles.spinnerPath} fill="#F3CA40" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p className={styles.errorText}>{error}</p>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={styles.container}>
      <div className={styles.viewModeButtons}>
        {(["organic", "radial", "hierarchical"] as const).map((mode) => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={cn(
              styles.viewModeButton,
              viewMode === mode && styles.viewModeButtonActive
            )}
          >
            {mode}
          </button>
        ))}
      </div>

      <div className={styles.canvasContainer}>
        <canvas
          ref={canvasRef}
          width={WIDTH}
          height={HEIGHT}
          className={styles.canvas}
          onMouseMove={handleMouseMove}
        />
      </div>

      <div className={styles.legend}>
        <div className={styles.legendItem}>
          <span className={cn(styles.legendDot, styles.legendDotEntity)} />
          Entity
        </div>
        <div className={styles.legendItem}>
          <span className={cn(styles.legendDot, styles.legendDotHigh)} />
          High Risk
        </div>
        <div className={styles.legendItem}>
          <span className={cn(styles.legendDot, styles.legendDotMedium)} />
          Medium Risk
        </div>
        <div className={styles.legendItem}>
          <span className={cn(styles.legendDot, styles.legendDotLow)} />
          Low Risk
        </div>
      </div>
    </div>
  );
}
