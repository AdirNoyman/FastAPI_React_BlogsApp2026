import { Navbar } from '@/components/Navbar';
import { PostCard } from '@/components/PostCard';
import { Sidebar } from '@/components/Sidebar';
import { usePosts } from '@/hooks/usePosts';

function App() {
  const { posts, loading, error } = usePosts();

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="container mx-auto px-4 py-6">
        {loading && (
          <div className="text-center py-8">Loading posts...</div>
        )}

        {error && (
          <div className="text-center py-8 text-red-500">
            Error: {error}
          </div>
        )}

        {!loading && !error && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {posts.map((post) => (
                <PostCard key={post.id} post={post} />
              ))}
            </div>
            <div>
              <Sidebar />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
