import React from 'react';

interface SkeletonProps {
  className?: string;
  lines?: number;
  width?: string;
  height?: string;
}

export function Skeleton({ className = '', width = 'w-full', height = 'h-4' }: SkeletonProps) {
  return (
    <div 
      className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${width} ${height} ${className}`}
    />
  );
}

export function SkeletonText({ lines = 3, className = '' }: { lines?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton 
          key={i} 
          width={i === lines - 1 ? 'w-3/4' : 'w-full'} 
        />
      ))}
    </div>
  );
}

export function SkeletonCard({ className = '' }: { className?: string }) {
  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow p-6 ${className}`}>
      <div className="space-y-4">
        <Skeleton height="h-6" width="w-1/2" />
        <SkeletonText lines={3} />
        <div className="flex space-x-4">
          <Skeleton height="h-10" width="w-20" />
          <Skeleton height="h-10" width="w-20" />
        </div>
      </div>
    </div>
  );
}