# Frontend - Real-Time Street Parking Detection

Modern React frontend built with Next.js for the parking detection application.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. **Install Dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env.local
   ```
   
   Edit `.env.local` with your configuration:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. **Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open Application**
   Visit [http://localhost:3000](http://localhost:3000)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                 # Next.js 13+ App Router
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Home page
│   ├── components/
│   │   ├── features/        # Feature-specific components
│   │   │   ├── VideoUpload.tsx
│   │   │   ├── ProcessingStatus.tsx
│   │   │   └── ResultsDisplay.tsx
│   │   └── ui/              # Reusable UI components
│   │       ├── Header.tsx
│   │       ├── VideoPlayer.tsx
│   │       └── StatisticsChart.tsx
│   ├── hooks/               # Custom React hooks
│   │   └── useApi.ts        # API interaction hooks
│   ├── utils/               # Utility functions
│   │   ├── api.ts           # API client
│   │   └── index.ts         # General utilities
│   ├── types/               # TypeScript definitions
│   │   └── index.ts         # Type definitions
│   └── styles/              # Styling files
│       └── globals.css      # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── next.config.js           # Next.js configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
```

## 🛠️ Technology Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Headless UI
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Forms**: React Hook Form
- **File Upload**: React Dropzone
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast

## 🎨 Features

### Video Upload
- Drag & drop interface
- File validation
- Upload progress tracking
- Processing configuration

### Real-time Processing
- Live status updates
- Progress visualization
- Error handling
- Cancellation support

### Results Display
- Interactive video player
- Statistics dashboard
- Data visualization
- Export functionality

### Responsive Design
- Mobile-first approach
- Touch-friendly interface
- Adaptive layouts
- Cross-browser compatibility

## 🔧 Configuration

### Environment Variables

Create `.env.local` file:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id
```

### API Integration

The frontend communicates with the FastAPI backend through:

- **Upload Endpoint**: `POST /api/v1/upload/`
- **Status Endpoint**: `GET /api/v1/processing/{job_id}`
- **Results Endpoint**: `GET /api/v1/results/{job_id}`
- **Statistics Endpoint**: `GET /api/v1/results/{job_id}/statistics`

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

## 🏗️ Building

### Development Build
```bash
npm run build
npm start
```

### Production Build
```bash
npm run build
```

### Static Export (for CDN deployment)
```bash
npm run build
npm run export
```

## 🚢 Deployment

### Render.com Deployment

1. **Connect Repository**
   - Link your GitHub repository to Render

2. **Configure Build Settings**
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Node Version**: 18+

3. **Environment Variables**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   ```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel --prod
   ```

### Docker Deployment

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 Performance Optimization

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: `npm run analyze`
- **Lazy Loading**: React.lazy for components
- **Memoization**: React.memo for expensive components

## 🎯 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📱 Mobile Support

- iOS Safari 14+
- Chrome Mobile 90+
- Samsung Internet 14+

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
