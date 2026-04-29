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

import {BookOpen, Github, ChevronDown, User, Bell, LogOut} from 'lucide-react';
import {GlobalSearch} from '@/components/global-search';
import {Button} from '@/components/ui/button';
import {Avatar, AvatarFallback} from '@/components/ui/avatar';
import {Tooltip, TooltipContent, TooltipProvider, TooltipTrigger} from '@/components/ui/tooltip';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger
} from '@/components/ui/dropdown-menu';

export function SiteHeader() {
    return (
        <header className="flex h-14 shrink-0 items-center justify-between px-5 border-b border-[rgba(255,255,255,0.07)] bg-background">
            {/* Left: logo + name */}
            <div className="flex items-center gap-2.5">
                <img src="/logo.png" alt="CASA" className="size-8" />
                <span className="text-base font-semibold text-foreground/90 tracking-tight">
                    Continuous Agent Semantic Authorization
                </span>
            </div>

            {/* Right: icons + user */}
            <div className="flex items-center gap-2">
                <GlobalSearch />
                <div className="w-px h-5 bg-[rgba(255,255,255,0.1)] mx-1" />
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                                asChild
                            >
                                <a
                                    href="https://sturdy-adventure-3qqek64.pages.github.io/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <BookOpen className="h-4 w-4" />
                                </a>
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>Documentation</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                                asChild
                            >
                                <a
                                    href="https://github.com/outshift-open/casa"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <Github className="h-4 w-4" />
                                </a>
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>GitHub</TooltipContent>
                    </Tooltip>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 cursor-pointer text-muted-foreground hover:text-foreground"
                                onClick={() =>
                                    window.dispatchEvent(new KeyboardEvent('keydown', {key: '?', bubbles: true}))
                                }
                            >
                                <kbd className="text-xs font-mono font-semibold">?</kbd>
                            </Button>
                        </TooltipTrigger>
                        <TooltipContent>Keyboard shortcuts</TooltipContent>
                    </Tooltip>
                </TooltipProvider>

                <div className="w-px h-5 bg-[rgba(255,255,255,0.1)] mx-1" />

                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <button
                            type="button"
                            className="group flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-accent data-[state=open]:bg-accent transition-colors cursor-pointer"
                        >
                            <Avatar className="h-8 w-8 rounded-lg">
                                <AvatarFallback className="rounded-lg bg-gradient-to-br from-[#006B8A] to-[#00BCEB] text-white font-bold">
                                    AS
                                </AvatarFallback>
                            </Avatar>
                            <div className="grid text-left text-sm leading-tight">
                                <span className="truncate font-semibold">Admin</span>
                                <span className="truncate text-xs text-muted-foreground">admin@casa.local</span>
                            </div>
                            <ChevronDown className="ml-auto size-4 text-muted-foreground transition-transform group-data-[state=open]:rotate-180" />
                        </button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="min-w-56 rounded-lg" side="bottom" align="end" sideOffset={6}>
                        <DropdownMenuLabel className="p-0 font-normal">
                            <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                                <Avatar className="h-8 w-8 rounded-lg">
                                    <AvatarFallback className="rounded-lg bg-gradient-to-br from-[#006B8A] to-[#00BCEB] text-white font-bold">
                                        AS
                                    </AvatarFallback>
                                </Avatar>
                                <div className="grid flex-1 text-left text-sm leading-tight">
                                    <span className="truncate font-semibold">Admin</span>
                                    <span className="truncate text-xs text-muted-foreground">admin@casa.local</span>
                                </div>
                            </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem disabled className="cursor-pointer">
                            <User className="mr-2 h-4 w-4" />
                            Account
                        </DropdownMenuItem>
                        <DropdownMenuItem disabled className="cursor-pointer">
                            <Bell className="mr-2 h-4 w-4" />
                            Notifications
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem disabled className="cursor-pointer">
                            <LogOut className="mr-2 h-4 w-4" />
                            Log out
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
}
