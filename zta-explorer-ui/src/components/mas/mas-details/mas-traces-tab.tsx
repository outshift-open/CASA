import {Card, CardContent} from '@/components/ui/card';
import {Activity} from 'lucide-react';

export function MASTracesTab() {
    return (
        <Card>
            <CardContent className="pt-6">
                <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="rounded-full bg-muted p-4 mb-4">
                        <Activity className="h-8 w-8 text-muted-foreground" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Traces Coming Soon</h3>
                    <p className="text-sm text-muted-foreground max-w-md">
                        Authorization traces and tool call monitoring will be available in a future release. This
                        feature will provide real-time insights into MAS activity, success rates, and performance
                        metrics.
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
