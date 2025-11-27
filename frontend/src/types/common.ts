export interface NewsItem {
  id: string;
  title: string;
  source: string;
  time: string;
  category: 'esg' | 'carbon' | 're100' | 'regulation';
}

export interface TaskItem {
  id: string;
  title: string;
  completed: boolean;
}

export interface ScheduleItem {
  id: string;
  date: string;
  time: string;
  title: string;
  status: 'done' | 'progress' | 'pending';
  progress: number;
  view: 'yearly' | 'monthly' | 'weekly';
  tasks: TaskItem[];
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  firstLogin: boolean;
}
