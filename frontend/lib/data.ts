// lib/data.ts


import type { FeatureCardProps } from "@/components/FeatureCard";

export const features: FeatureCardProps[] = [
  {
    icon: 'FaLayerGroup',
    title: 'Layout Grouping Demo',
    description:
      'Visualize and experiment with CSS layout techniques. Our interactive tool helps you understand how elements position and behave in various layout systems.',
  },
  {
    icon: 'FaPuzzlePiece',
    title: 'Coding Quizzes',
    description:
      'Test your knowledge with our comprehensive quizzes covering multiple programming languages and concepts. Track your progress and identify areas for improvement.',
  },
  {
    icon: 'FaGamepad',
    title: 'Learning Games',
    description:
      'Make learning fun with our programming games. Solve puzzles, debug code, and complete challenges while improving your coding skills.',
  },
  {
    icon: 'FaCode',
    title: 'Code Practice',
    description:
      'Sharpen your skills with our extensive collection of coding exercises. Get instant feedback and suggestions for improvement.',
  },
];

export const testimonials = [
  {
    id: 1,
    text: '"The layout grouping tool completely changed how I understand CSS. I finally grasped flexbox and grid after just a few hours of experimentation!"',
    author: 'Sarah Andrews',
    role: 'Frontend Developer',
    initials: 'SA',
  },
  {
    id: 2,
    text: '"I\'ve tried many coding platforms, but the gamified learning approach here kept me engaged. I actually look forward to practicing now!"',
    author: 'Michael Johnson',
    role: 'Computer Science Student',
    initials: 'MJ',
  },
  {
    id: 3,
    text: '"As a senior developer, I use CodeCraft to keep my skills sharp. The advanced challenges are exactly what I needed to stay current with new technologies."',
    author: 'Robert Parker',
    role: 'Lead Developer',
    initials: 'RP',
  },
];

export const steps = [
  {
    title: 'Create an Account',
    description:
      'Sign up for free and set up your learning profile based on your interests and skill level.',
  },
  {
    title: 'Choose Your Path',
    description:
      'Select from our various learning modules based on your goals and programming interests.',
  },
  {
    title: 'Start Learning',
    description:
      'Dive into interactive lessons, challenges, and projects that make learning engaging and effective.',
  },
];













// lib/colorData.ts
export const colorPalettes = [
  {
    name: 'Ocean Breeze',
    description: 'Cool and refreshing colors reminiscent of the sea and sky',
    colors: ['#2c3e50', '#3498db', '#e74c3c', '#ecf0f1'],
  },
  {
    name: 'Vibrant Harmony',
    description: 'Bold and energetic colors that complement each other',
    colors: ['#8e44ad', '#f1c40f', '#16a085', '#f5f5f5'],
  },
  {
    name: 'Earth Tones',
    description: 'Natural colors inspired by the environment',
    colors: ['#34495e', '#e67e22', '#2ecc71', '#f9f9f9'],
  },
  {
    name: 'Primary Contrast',
    description: 'Strong primary colors with clear visual hierarchy',
    colors: ['#2980b9', '#c0392b', '#27ae60', '#f7f7f7'],
  },
];

export const colorGuidelines = [
  {
    icon: '🎨',
    title: 'Color Hierarchy',
    description: 'Establish a clear visual hierarchy by using your primary color for main actions, secondary color for secondary actions, and accent colors for highlights.',
  },
  {
    icon: '👁️',
    title: 'Accessibility',
    description: 'Ensure sufficient contrast between text and background colors. Use tools to check contrast ratios to make your designs accessible to everyone.',
  },
  {
    icon: '🔄',
    title: 'Consistency',
    description: 'Maintain consistency in your color usage across all components and screens. Create a style guide to document your color choices.',
  },
];











// lib/teamData.ts
export const teamMembers = [
  {
    name: 'Zara',
    role: 'Frontend Development',
    image: '/images/higab.jpg',
    description: 'Learning to build website user interfaces and implementing APIs',
    skills: ['HTML', 'CSS', 'JavaScript', 'Creativity'],
    progress: [
      { label: 'HTML', value: 75 },
      { label: 'CSS Layout', value: 65 },
      { label: 'JavaScript', value: 30 },
    ],
  },
  {
    name: 'Ayyub',
    role: 'Mentor & Guide',
    image: '/images/admin.png',
    description: 'Helping others connect coding concepts with fun projects.',
    skills: ['Mentorship', 'JavaScript', 'TypeScript', 'React', 'Python'],
    progress: [
      { label: 'AI Concepts', value: 90 },
      { label: 'Full-Stack Development', value: 95 },
      { label: 'AI Engineering', value: 65 },
      { label: 'Agentics', value: 55 },

    ],
  },
  {
    name: 'DevTribe Crew',
    role: 'Fellow Learners',
    image: '/images/git2.jpg',
    description: 'Coding, building, and sharing ideas together.',
    skills: ['Collaboration', 'Projects', 'Community'],
    progress: [
      { label: 'Team Projects', value: 20 },
      { label: 'Collaboration', value: 30 },
    ],
  },
  {
    name: 'Muiz',
    role: 'Frontend Development Student',
    image: '/images/user.jpg',
    description: 'Exploring modern web technologies and responsive design.',
    skills: ['HTML', 'CSS', 'JavaScript', 'React'],
    progress: [
      { label: 'Frontend Basics', value: 85 },
      { label: 'React Fundamentals', value: 40 },
      { label: 'Responsive Design', value: 70 },
    ],
  },
  {
    name: 'David',
    role: 'Frontend Development Student',
    image: '/images/admin2.png',
    description: 'Passionate about creating beautiful user interfaces.',
    skills: ['UI Design', 'CSS', 'JavaScript', 'Accessibility'],
    progress: [
      { label: 'UI Design', value: 80 },
      { label: 'CSS Mastery', value: 90 },
      { label: 'JavaScript', value: 60 },
    ],
  },
  {
    name: 'Romlah_Dev',
    role: 'Frontend Developer JS',
    image: '/images/hijab.png',
    description: 'Specializing in JavaScript and modern frameworks.',
    skills: ['JavaScript', 'React', 'Next.js', 'TypeScript'],
    progress: [
      { label: 'JavaScript', value: 95 },
      { label: 'React Ecosystem', value: 85 },
      { label: 'TypeScript', value: 70 },
    ],
  },
  {
    name: 'Iremide',
    role: 'UI/UX',
    image: '/images/hijab.png',
    description: 'Website User Interface and Experience Design.',
    skills: ['Figma', 'Web Design'],
    progress: [
      { label: 'Figma', value: 65 },
      { label: 'Web Design', value: 85 },
    ],
  },
  {
    name: 'Uthman',
    role: 'Explorer/Developer',
    image: '/images/user.jpg',
    description: 'Exploring various programming paradigms and tools.',
    skills: ['Python', 'JavaScript', 'Algorithms', 'Problem Solving'],
    progress: [
      { label: 'Python', value: 75 },
      { label: 'Algorithms', value: 65 },
      { label: 'Web Development', value: 50 },
    ],
  },
];