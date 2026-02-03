import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import {Button} from '@/components/ui/button';

interface ApplicationDeleteDialogProps {
    open: boolean;
    isPending: boolean;
    appName?: string;
    onClose: () => void;
    onConfirm: () => void;
}

export function ApplicationDeleteDialog({open, isPending, appName, onClose, onConfirm}: ApplicationDeleteDialogProps) {
    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Delete Application</DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete
                        {appName ? (
                            <>
                                {' '}
                                <span className="font-semibold text-foreground">{appName}</span>
                            </>
                        ) : (
                            ' this application'
                        )}
                        ? This action cannot be undone.
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
