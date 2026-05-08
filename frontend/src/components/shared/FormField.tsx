import { forwardRef, type InputHTMLAttributes } from 'react';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const FormField = forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, error, id, className = '', ...props }, ref) => {
    const inputId = id || `input-${label.replace(/\s+/g, '-').toLowerCase()}`;

    return (
      <div className={`flex flex-col space-y-1.5 w-full ${className}`}>
        <label htmlFor={inputId} className="text-sm font-semibold text-gray-700">
          {label}
        </label>
        
        <input
          ref={ref}
          id={inputId}
          className={`
            px-4 py-2.5 rounded-lg border bg-white
            focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500
            transition-all duration-200
            ${error ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500' : 'border-gray-300'}
          `}
          {...props}
        />
        
        {error && (
          <span className="text-xs font-medium text-red-500 mt-1">
            {error}
          </span>
        )}
      </div>
    );
  }
);

FormField.displayName = 'FormField';
