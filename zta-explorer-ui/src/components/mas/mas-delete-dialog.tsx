import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import {Button} from '@/components/ui/button';

interface MASDeleteDialogProps {
    open: boolean;
    isPending: boolean;
    masName?: string;
    onClose: () => void;
    onConfirm: () => void;
}

export function MASDeleteDialog({open, isPending, masName, onClose, onConfirm}: MASDeleteDialogProps) {
    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Delete MAS</DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete
                        {masName ? (
                            <>
                                {' '}
                                <span className="font-semibold text-foreground">{masName}</span>
                            </>
                        ) : (
                            ' this MAS'
                        )}
                        ? This will also delete all applications in this MAS. This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button type="button" variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                    <Button type="button" variant="destructive" onClick={onConfirm} disabled={isPending}>
                        {isPending ? 'Deleting...' : 'Delete'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
