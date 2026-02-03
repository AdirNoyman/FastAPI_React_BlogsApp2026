import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ThemeToggle';

export function Navbar() {
  return (
    <nav className="h-12 bg-[hsl(var(--nav-bg))] border-b border-border flex items-center px-4 sticky top-0 z-50">
      <div className="flex items-center gap-6 flex-1">
        <span className="font-semibold text-lg">FastAPI Blog</span>
        <a href="/" className="hover:text-primary transition-colors">
          Home
        </a>
      </div>
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <Button variant="outline" size="sm">
          Login
        </Button>
        <Button variant="outline" size="sm">
          Register
        </Button>
      </div>
    </nav>
  );
}
