import type { Post } from '@/types/post';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';

interface PostCardProps {
  post: Post;
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function PostCard({ post }: PostCardProps) {
  const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(
    post.author
  )}&background=random&size=40`;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-3 pb-3">
        <Avatar className="h-10 w-10">
          <AvatarImage src={avatarUrl} alt={post.author} />
          <AvatarFallback>{getInitials(post.author)}</AvatarFallback>
        </Avatar>
        <div className="flex flex-col">
          <a href="#" className="text-sky-400 hover:underline text-sm font-medium">
            {post.author}
          </a>
          <span className="text-xs text-muted-foreground">{post.date_posted}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <h2 className="text-xl font-semibold hover:underline cursor-pointer">
          {post.title}
        </h2>
        <p className="text-muted-foreground text-sm">{post.content}</p>
      </CardContent>
    </Card>
  );
}
