// lib/types.ts
export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isActive: boolean;
}

export interface UserProfile {
  id: string;
  userId: string;
  role: string;
  registeredCourses: string[];
  createdAt: string;
}


export interface UserCourse {
  id: string;
  userId: string;
  courseSlug: string;
  category: string;
  difficulty: string;
  progress: number;
  completed: boolean;
  lastAccessed: string | null;
  enrolledAt: string;
}

export interface QuizQuestion {
  id: string;
  quizId: string;
  question: string;
  options: string[];
  correctAnswer?: string;
  explanation: string;
  points: number;
  questionType: 'single' | 'multiple';
  timeLimit: number;
}

export interface QuizWithDetails {
  id: string;
  title: string;
  courseSlug?: string;
  totalQuestions?: number;
  duration?: number; // seconds
}

export interface QuizAttempt {
  id: string;
  userId: string;
  quizId: string;
  courseSlug?: string;
  score: number;
  passed: boolean;
  attemptedAt: string;
}


export interface CourseCatalog {
  id: string;
  slug: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration: number;
  totalQuizzes: number;
  totalLessons: number;
  instructor: string;
  prerequisites: string[];
  tags: string[];
  thumbnail: string;
  createdAt: string;
}


export interface GameProgress {
  id: string;
  userId: string;
  gameId: string;
  level: number;
  xp: number;
  lastPlayed: string | null;
}

export interface AuthResponse {
  message: string;
  data: User;
}

export interface ApiResponse<T> {
  message: string;
  data: T;
}

export interface LoginCredentials {
  email: string;
  password: string;
}


export interface RegisterCredentials {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role?: string;
}

export interface QuizSubmission {
  quizId: string;
  score: number;
  courseSlug?: string;
}


export interface CourseEnrollment {
  courseSlug: string;
  category?: string;
  difficulty?: string;
}




export interface Feature {
  icon: string;
  title: string;
  description: string;
}

export interface Testimonial {
  id: number;
  text: string;
  author: string;
  role: string;
  initials: string;
}

export interface ColorPalette {
  name: string;
  description: string;
  colors: string[];
}

export interface Profile {
  name: string;
  role: string;
  image: string;
  skills: string[];
  progress: {
    label: string;
    value: number;
  }[];
}






export interface AdminStats {
  totalUsers: number;
  totalCourses: number;
  totalQuizzes: number;
  totalQuestions: number;
  activeUsers: number;
  recentRegistrations: number;
  averageProgress: number;
}



export interface UserWithDetails extends User {
  createdAt: string;
  lastLogin: string | null;
  coursesCount: number;
  quizAttempts: number;
}

export interface QuestionWithDetails extends QuizQuestion {
  difficulty: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  isActive: boolean;
}

export interface CourseWithDetails extends CourseCatalog {
  enrolledCount: number;
  averageRating: number;
  completionRate: number;
  isPublished: boolean;
}



export interface AdminFilters {
  startDate?: string;
  endDate?: string;
  role?: string;
  status?: string;
  category?: string;
  difficulty?: string;
  search?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string | string[];
    borderColor: string | string[];
    borderWidth: number;
  }[];
}


export interface RecentActivity {
  id: string;
  userId: string;
  userName: string;
  action: string;
  target: string;
  timestamp: string;
  icon: string;
}