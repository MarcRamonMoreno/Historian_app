import React from "react";

const Alert = React.forwardRef(({ className, variant = "default", ...props }, ref) => (
  <div
    ref={ref}
    role="alert"
    className={`p-4 rounded-lg border ${
      variant === "destructive" 
        ? "bg-red-50 border-red-200 text-red-800" 
        : "bg-white border-gray-200"
    } ${className}`}
    {...props}
  />
));

Alert.displayName = "Alert";

const AlertDescription = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={`text-sm mt-1 ${className}`}
    {...props}
  />
));

AlertDescription.displayName = "AlertDescription";

export { Alert, AlertDescription };