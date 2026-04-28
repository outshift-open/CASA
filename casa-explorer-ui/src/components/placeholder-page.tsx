/**
 * Copyright 2026 Copyright 2026 Cisco Systems, Inc. and its affiliates
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {Card, CardContent} from '@/components/ui/card';

interface PlaceholderPageProps {
    title: string;
    description?: string;
    icon?: React.ComponentType<{className?: string}>;
}

export function PlaceholderPage({title, description, icon: Icon}: PlaceholderPageProps) {
    return (
        <div className="flex flex-1 items-center justify-center">
            <Card className="w-full">
                <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                    {Icon && (
                        <div className="mb-4 rounded-full bg-muted p-4">
                            <Icon className="h-8 w-8 text-muted-foreground" />
                        </div>
                    )}
                    <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
                    {description && <p className="mt-3 text-sm text-muted-foreground max-w-sm">{description}</p>}
                    <div className="mt-6 flex gap-2">
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse" />
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse [animation-delay:0.2s]" />
                        <div className="h-2 w-2 rounded-full bg-muted-foreground/40 animate-pulse [animation-delay:0.4s]" />
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
