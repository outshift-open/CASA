import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Label} from '@/components/ui/label';
import {AlertTriangle} from 'lucide-react';
import {useState} from 'react';

interface MASDeleteDialogProps {
    open: boolean;
    isPending: boolean;
    masName?: string;
    appCount?: number;
    onClose: () => void;
    onConfirm: () => void;
}

export function MASDeleteDialog({open, isPending, masName, appCount, onClose, onConfirm}: MASDeleteDialogProps) {
    const [confirmText, setConfirmText] = useState('');

    const handleClose = () => {
        setConfirmText('');
        onClose();
    };

    const handleConfirm = () => {
        if (confirmText === masName) {
            onConfirm();
            setConfirmText('');
        }
    };

    const isConfirmValid = confirmText === masName;

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-destructive" />
                        Delete MAS
                    </DialogTitle>
                    <DialogDescription className="space-y-2">
                        <p>
                            Are you sure you want to delete
                            {masName ? (
                                <>
                                    {' '}
                                    <span className="font-semibold text-foreground">{masName}</span>
                                </>
                            ) : (
                                ' this MAS'
                            )}
                            ?
                        </p>
                        {appCount !== undefined && appCount > 0 && (
                            <p className="text-destructive font-medium">
                                This will permanently delete {appCount}{' '}
                                {appCount === 1 ? 'application' : 'applications'} in this MAS.
                            </p>
                        )}
                        <p>This action cannot be undone.</p>
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-2">
                    <Label htmlFor="confirm-name" className="text-sm">
                        Type <span className="font-mono font-semibold">{masName}</span> to confirm:
                    </Label>
                    <Input
                        id="confirm-name"
                        value={confirmText}
                        onChange={(e) => setConfirmText(e.target.value)}
                        placeholder={masName}
                        disabled={isPending}
                        autoComplete="off"
                    />
                </div>
                <DialogFooter>
                    <Button type="button" variant="outline" onClick={handleClose} disabled={isPending}>
                        Cancel
                    </Button>
                    <Button
                        type="button"
                        variant="destructive"
                        onClick={handleConfirm}
                        disabled={isPending || !isConfirmValid}
                    >
                        {isPending ? 'Deleting...' : 'Delete MAS'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
