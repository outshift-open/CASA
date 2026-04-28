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

import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/components/ui/card';
import {Button} from '@/components/ui/button';
import {FileQuestion, Home} from 'lucide-react';
import {useNavigate} from 'react-router-dom';

export function NotFoundPage() {
    const navigate = useNavigate();

    return (
        <div className="flex flex-1 items-center justify-center">
            <Card className="w-full">
                <CardHeader className="text-center">
                    <div className="flex justify-center mb-4">
                        <div className="rounded-full bg-muted p-4">
                            <FileQuestion className="h-12 w-12 text-muted-foreground" />
                        </div>
                    </div>
                    <CardTitle className="text-3xl font-bold">404</CardTitle>
                    <CardDescription className="text-base">Page Not Found</CardDescription>
                </CardHeader>
                <CardContent className="text-center space-y-4">
                    <p className="text-sm text-muted-foreground">
                        The page you're looking for doesn't exist or has been moved.
                    </p>
                    <Button onClick={() => navigate('/')} className="gap-2">
                        <Home className="h-4 w-4" />
                        Back to Dashboard
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
