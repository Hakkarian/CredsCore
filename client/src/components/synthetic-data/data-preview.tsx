"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { SyntheticRecord } from "@/lib/api";
import { ShimmerBorder } from "@/components/ui/shimmer-tilt-card";
import styles from "./data-preview.module.scss";

interface DataPreviewProps {
  records: SyntheticRecord[];
  totalCount: number;
}

const DISPLAY_COLUMNS = [
  "RevolvingUtilizationOfUnsecuredLines",
  "age",
  "DebtRatio",
  "MonthlyIncome",
  "NumberOfTime30_59DaysPastDueNotWorse",
  "NumberOfOpenCreditLinesAndLoans",
  "NumberOfTimes90DaysLate",
  "NumberRealEstateLoansOrLines",
  "NumberOfTime60_89DaysPastDueNotWorse",
  "NumberOfDependents",
];

const SHORT_COLUMN_NAMES: Record<string, string> = {
  RevolvingUtilizationOfUnsecuredLines: "Util",
  NumberOfTime30_59DaysPastDueNotWorse: "30-59d",
  NumberOfOpenCreditLinesAndLoans: "OpenLines",
  NumberOfTimes90DaysLate: "90dLate",
  NumberRealEstateLoansOrLines: "RealEstate",
  NumberOfTime60_89DaysPastDueNotWorse: "60-89d",
  NumberOfDependents: "Deps",
};

export function DataPreview({ records, totalCount }: DataPreviewProps) {
  const [page, setPage] = useState(0);
  const pageSize = 10;
  const totalPages = Math.ceil(records.length / pageSize);
  const pageRecords = records.slice(page * pageSize, (page + 1) * pageSize);

  // Determine which columns are actually present in the data
  const presentColumns = records.length > 0
    ? DISPLAY_COLUMNS.filter(col => col in records[0])
    : DISPLAY_COLUMNS;

  return (
    <ShimmerBorder borderRadius="1rem">
      <div className={styles.container}>
        <div className={styles.headerRow}>
          <h3 className={styles.title}>Data Preview</h3>
          <span className={styles.totalCount}>
            {totalCount} records total
          </span>
        </div>

        {/* Table */}
        <div className={styles.tableWrapper}>
          <table className={styles.table}>
            <thead>
              <tr className={styles.tableHead}>
                <th className={styles.thIndex}>#</th>
                {presentColumns.map((col) => (
                  <th key={col} className={styles.thCell}>
                    {SHORT_COLUMN_NAMES[col] || col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pageRecords.map((record, i) => (
                <tr key={i} className={styles.tableRow}>
                  <td className={styles.tdIndex}>{page * pageSize + i + 1}</td>
                  {presentColumns.map((col) => (
                    <td key={col} className={styles.tdCell}>
                      {record[col] !== undefined && record[col] !== null
                        ? typeof record[col] === "number"
                          ? record[col].toFixed(col === "age" || col === "NumberOfDependents" || col === "NumberOfOpenCreditLinesAndLoans" || col === "NumberRealEstateLoansOrLines" ? 0 : 3)
                          : String(record[col])
                        : "-"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className={styles.pagination}>
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className={cn(
                page === 0 ? styles.pageButtonDisabled : styles.pageButton
              )}
            >
              Previous
            </button>
            <span className={styles.pageInfo}>
              Page {page + 1} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
              disabled={page >= totalPages - 1}
              className={cn(
                page >= totalPages - 1 ? styles.pageButtonDisabled : styles.pageButton
              )}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </ShimmerBorder>
  );
}
