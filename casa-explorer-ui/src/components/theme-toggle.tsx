import {Moon, Sun, Waves, Check} from 'lucide-react';
import {useTheme} from 'next-themes';
import {Button} from '@/components/ui/button';
import {DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger} from '@/components/ui/dropdown-menu';

const THEMES = [
    {value: 'light', label: 'Light', icon: Sun},
    {value: 'dark', label: 'Dark', icon: Moon},
    {value: 'ioc', label: 'IOC', icon: Waves}
] as const;

function CurrentIcon({theme}: {theme: string | undefined}) {
    const entry = THEMES.find((t) => t.value === theme) ?? THEMES[1];
    const Icon = entry.icon;
    return <Icon className="h-[1.2rem] w-[1.2rem]" />;
}

export function ThemeToggle() {
    const {theme, setTheme} = useTheme();

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9" title="Change theme">
                    <CurrentIcon theme={theme} />
                    <span className="sr-only">Change theme</span>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                {THEMES.map(({value, label, icon: Icon}) => (
                    <DropdownMenuItem
                        key={value}
                        onClick={() => setTheme(value)}
                        className="flex items-center gap-2 cursor-pointer"
                    >
                        <Icon className="h-4 w-4" />
                        <span>{label}</span>
                        {theme === value && <Check className="h-3.5 w-3.5 ml-auto text-primary" />}
                    </DropdownMenuItem>
                ))}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
