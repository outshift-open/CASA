import {useState} from 'react';
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

interface ScopeDeleteDialogProps {
    open: boolean;
    isPending: boolean;
    scopeName?: string;
    onClose: () => void;
    onConfirm: () => void;
}

export function ScopeDeleteDialog({open, isPending, scopeName, onClose, onConfirm}: ScopeDeleteDialogProps) {
    const [confirmText, setConfirmText] = useState('');

    const isConfirmValid = confirmText === scopeName;

    const handleClose = () => {
        setConfirmText('');
        onClose();
    };

    const handleConfirm = () => {
        if (isConfirmValid) {
            onConfirm();
            setConfirmText('');
        }
    };

    return (
        <Dialog open={open} onOpenChange={handleClose}>
            <DialogContent>
                <DialogHeader>
                    <div className="flex items-center gap-2">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10">
                            <AlertTriangle className="h-5 w-5 text-destructive" />
                        </div>
                        <DialogTitle>Delete Scope</DialogTitle>
                    </div>
                    <DialogDescription className="space-y-2 pt-2">
                        <p>
                            Are you sure you want to delete
                            {scopeName ? (
                                <>
                                    {' '}
                                    <span className="font-semibold text-foreground">{scopeName}</span>
                                </>
                            ) : (
                                ' this scope'
                            )}
                            ?
                        </p>
                        <p className="text-destructive font-medium">
                            This action cannot be undone. The scope will be removed from Keycloak and all associated
                            applications.
                        </p>
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-2 py-4">
                    <Label htmlFor="confirm-name">
                        Type <span className="font-semibold">{scopeName}</span> to confirm
                    </Label>
                    <Input
                        id="confirm-name"
                        value={confirmText}
                        onChange={(e) => setConfirmText(e.target.value)}
                        placeholder={scopeName}
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
                        {isPending ? 'Deleting...' : 'Delete Scope'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
