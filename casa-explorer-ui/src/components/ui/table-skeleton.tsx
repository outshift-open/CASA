import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table';
import {Skeleton} from '@/components/ui/skeleton';

interface TableSkeletonProps {
    rows?: number;
    columns?: number;
    showSearch?: boolean;
    showPagination?: boolean;
}

export function TableSkeleton({rows = 5, columns = 5, showSearch = true, showPagination = true}: TableSkeletonProps) {
    return (
        <div className="space-y-4">
            {showSearch && <Skeleton className="h-10 w-full" />}
            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            {Array.from({length: columns}).map((_, i) => (
                                <TableHead key={i}>
                                    <Skeleton className="h-8 w-20" />
                                </TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {Array.from({length: rows}).map((_, rowIndex) => (
                            <TableRow key={rowIndex}>
                                {Array.from({length: columns}).map((_, colIndex) => (
                                    <TableCell key={colIndex}>
                                        <Skeleton className="h-4 w-full max-w-[200px]" />
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
            {showPagination && (
                <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-24" />
                    <div className="flex items-center gap-2">
                        <Skeleton className="h-9 w-24" />
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-9 w-20" />
                    </div>
                </div>
            )}
        </div>
    );
}
