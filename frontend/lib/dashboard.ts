
// lib/types/dashboard.ts
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'instructor' | 'student';
  avatar?: string;
  joinedAt: Date;
  isActive: boolean;
  lastLogin?: Date;
}

export interface Course {
  id: string;
  title: string;
  description: string;
  category: 'html' | 'css' | 'javascript' | 'react' | 'typescript' | 'nextjs';
  level: 'beginner' | 'intermediate' | 'advanced';
  duration: number; // in hours
  students: number;
  rating: number;
  status: 'draft' | 'published' | 'archived';
  createdAt: Date;
  updatedAt: Date;
}

export interface Quiz {
  id: string;
  title: string;
  courseId: string;
  totalQuestions: number;
  passingScore: number;
  attempts: number;
  averageScore: number;
  status: 'draft' | 'published';
  createdAt: Date;
}

export interface Analytics {
  totalUsers: number;
  activeUsers: number;
  totalCourses: number;
  totalQuizzes: number;
  completionRate: number;
  revenue?: number;
  userGrowth: number;
  quizAttempts: number;
}

export interface Activity {
  id: string;
  userId: string;
  userName: string;
  action: string;
  target: string;
  timestamp: Date;
  ip?: string;
}

export interface Progress {
  userId: string;
  courseId: string;
  completedLessons: number;
  totalLessons: number;
  quizScores: number[];
  lastActivity: Date;
}