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
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from '@/components/ui/select';
import {Textarea} from '@/components/ui/textarea';
import type {App, AppType} from '@/types/app.types';

interface ApplicationFormDialogProps {
    open: boolean;
    app: App | null;
    isPending: boolean;
    onClose: () => void;
    onSubmit: (data: {type: AppType; name: string; base_url: string; tools: string[]}) => void;
}

export function ApplicationFormDialog({open, app, isPending, onClose, onSubmit}: ApplicationFormDialogProps) {
    const getInitialFormData = () => ({
        type: (app?.type || 'agent') as AppType,
        name: app?.name || '',
        base_url: app?.base_url || '',
        tools: app?.tools?.join(', ') || ''
    });

    const [formData, setFormData] = useState(getInitialFormData);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const tools = formData.tools
            .split(',')
            .map((tool) => tool.trim())
            .filter((tool) => tool.length > 0);

        onSubmit({
            type: formData.type,
            name: formData.name,
            base_url: formData.base_url,
            tools
        });
    };

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent>
                <form onSubmit={handleSubmit}>
                    <DialogHeader>
                        <DialogTitle>{app ? 'Edit Application' : 'Add Application'}</DialogTitle>
                        <DialogDescription>
                            {app
                                ? 'Update the application details below.'
                                : 'Fill in the details to create a new application.'}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-6 py-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name" className="text-sm font-medium">
                                Name <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="name"
                                placeholder="Enter application name"
                                value={formData.name}
                                onChange={(e) => setFormData({...formData, name: e.target.value})}
                                required
                                className="w-full"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="type" className="text-sm font-medium">
                                Type <span className="text-destructive">*</span>
                            </Label>
                            <Select
                                value={formData.type}
                                onValueChange={(value: AppType) => setFormData({...formData, type: value})}
                            >
                                <SelectTrigger id="type" className="w-full">
                                    <SelectValue placeholder="Select application type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="agent">Agent</SelectItem>
                                    <SelectItem value="client">Client</SelectItem>
                                    <SelectItem value="mcp_server">MCP Server</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="base_url" className="text-sm font-medium">
                                Base URL <span className="text-destructive">*</span>
                            </Label>
                            <Input
                                id="base_url"
                                type="url"
                                placeholder="https://example.com/api"
                                value={formData.base_url}
                                onChange={(e) => setFormData({...formData, base_url: e.target.value})}
                                required
                                className="w-full"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="tools" className="text-sm font-medium">
                                Tools <span className="text-muted-foreground text-xs">(optional)</span>
                            </Label>
                            <Textarea
                                id="tools"
                                placeholder="Enter tools separated by commas&#10;Example: tool1, tool2, tool3"
                                value={formData.tools}
                                onChange={(e) => setFormData({...formData, tools: e.target.value})}
                                className="w-full min-h-[80px] resize-none"
                                rows={3}
                            />
                            <p className="text-xs text-muted-foreground">Separate multiple tools with commas</p>
                        </div>
                    </div>
                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={onClose}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={isPending}>
                            {isPending ? 'Saving...' : app ? 'Update' : 'Create'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
