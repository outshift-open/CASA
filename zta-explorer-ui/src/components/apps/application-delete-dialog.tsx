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

interface ApplicationDeleteDialogProps {
    open: boolean;
    isPending: boolean;
    appName?: string;
    onClose: () => void;
    onConfirm: () => void;
}

export function ApplicationDeleteDialog({open, isPending, appName, onClose, onConfirm}: ApplicationDeleteDialogProps) {
    const [confirmText, setConfirmText] = useState('');

    const isConfirmValid = confirmText === appName;

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
                        <DialogTitle>Delete Application</DialogTitle>
                    </div>
                    <DialogDescription className="space-y-2 pt-2">
                        <p>
                            Are you sure you want to delete
                            {appName ? (
                                <>
                                    {' '}
                                    <span className="font-semibold text-foreground">{appName}</span>
                                </>
                            ) : (
                                ' this application'
                            )}
                            ?
                        </p>
                        <p className="text-destructive font-medium">This action cannot be undone.</p>
                    </DialogDescription>
                </DialogHeader>
                <div className="space-y-2 py-4">
                    <Label htmlFor="confirm-name">
                        Type <span className="font-semibold">{appName}</span> to confirm
                    </Label>
                    <Input
                        id="confirm-name"
                        value={confirmText}
                        onChange={(e) => setConfirmText(e.target.value)}
                        placeholder={appName}
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
                        {isPending ? 'Deleting...' : 'Delete Application'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
