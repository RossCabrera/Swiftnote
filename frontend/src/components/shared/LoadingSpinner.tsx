interface LoadingSpinnerProps {
  size?: string;
  className?: string;
  fullScreen?: boolean;
}

export const LoadingSpinner = ({ 
  size = "h-8 w-8", 
  className = "",
  fullScreen = false
}: LoadingSpinnerProps) => {
  const spinner = (
    <svg 
      className={`animate-spin text-blue-600 ${size} ${className}`} 
      xmlns="http://www.w3.org/2000/svg" 
      fill="none" 
      viewBox="0 0 24 24"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  );

  if (fullScreen) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-gray-50 absolute inset-0 z-50">
        <div className="flex flex-col items-center gap-4">
          {spinner}
          <span className="text-gray-500 font-medium animate-pulse">Checking authentication...</span>
        </div>
      </div>
    );
  }

  return spinner;
};
