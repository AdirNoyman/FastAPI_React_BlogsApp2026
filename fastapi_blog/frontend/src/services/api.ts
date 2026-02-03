import type { Post } from '@/types/post';

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000/api' : '/api';

export async function getPosts(): Promise<Post[]> {
  const response = await fetch(`${API_BASE}/posts`);
  if (!response.ok) {
    throw new Error('Failed to fetch posts');
  }
  return response.json();
}

export async function getPost(id: number): Promise<Post> {
  const response = await fetch(`${API_BASE}/posts/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch post');
  }
  return response.json();
}
