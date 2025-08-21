import React from 'react';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Skeleton,
  Paper
} from '@mui/material';

interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  showHeader?: boolean;
}

const TableSkeleton: React.FC<TableSkeletonProps> = ({ 
  rows = 5, 
  columns = 4,
  showHeader = true 
}) => {
  const skeletonRows = Array.from({ length: rows }, (_, index) => index);
  const skeletonCols = Array.from({ length: columns }, (_, index) => index);

  return (
    <TableContainer component={Paper}>
      <Table>
        {showHeader && (
          <TableHead>
            <TableRow>
              {skeletonCols.map((col) => (
                <TableCell key={col}>
                  <Skeleton variant="text" width="60%" height={24} />
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
        )}
        <TableBody>
          {skeletonRows.map((row) => (
            <TableRow key={row}>
              {skeletonCols.map((col) => (
                <TableCell key={col}>
                  <Skeleton 
                    variant="text" 
                    width={col === 0 ? "80%" : "60%"} 
                    height={20} 
                  />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TableSkeleton;