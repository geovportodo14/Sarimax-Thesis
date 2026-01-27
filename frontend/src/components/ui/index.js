import React from 'react';

// =============================================================================
// CARD COMPONENT
// =============================================================================
export function Card({ children, className = '', hover = true, ...props }) {
  return (
    <div
      className={`
        bg-white rounded-2xl border border-surface-100
        ${hover ? 'shadow-card hover:shadow-card-hover transition-shadow duration-200' : 'shadow-card'}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '', action }) {
  return (
    <div className={`flex items-start justify-between gap-4 ${className}`}>
      <div className="flex-1">{children}</div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}

export function CardBody({ children, className = '' }) {
  return (
    <div className={`p-5 sm:p-6 ${className}`}>
      {children}
    </div>
  );
}

// =============================================================================
// SECTION HEADER COMPONENT
// =============================================================================
export function SectionHeader({ icon, title, subtitle, action, className = '' }) {
  return (
    <div className={`flex items-start justify-between gap-4 mb-5 ${className}`}>
      <div className="flex items-center gap-3">
        {icon && (
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary-50 text-primary-600">
            {icon}
          </div>
        )}
        <div>
          <h3 className="text-heading-lg text-surface-900">{title}</h3>
          {subtitle && (
            <p className="text-body-sm text-surface-500 mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>
      {action && <div className="flex-shrink-0">{action}</div>}
    </div>
  );
}

// =============================================================================
// STAT TILE COMPONENT
// =============================================================================
export function StatTile({ 
  label, 
  value, 
  unit, 
  icon, 
  trend, 
  trendLabel,
  variant = 'default', // default, success, warning, danger, info
  size = 'md', // sm, md, lg
  className = '' 
}) {
  const variantStyles = {
    default: 'bg-surface-50 border-surface-100',
    success: 'bg-emerald-50 border-emerald-100',
    warning: 'bg-amber-50 border-amber-100',
    danger: 'bg-red-50 border-red-100',
    info: 'bg-blue-50 border-blue-100',
    primary: 'bg-primary-50 border-primary-100',
  };

  const valueStyles = {
    default: 'text-surface-900',
    success: 'text-emerald-700',
    warning: 'text-amber-700',
    danger: 'text-red-700',
    info: 'text-blue-700',
    primary: 'text-primary-700',
  };

  const iconStyles = {
    default: 'text-surface-400',
    success: 'text-emerald-500',
    warning: 'text-amber-500',
    danger: 'text-red-500',
    info: 'text-blue-500',
    primary: 'text-primary-500',
  };

  const sizeStyles = {
    sm: { container: 'p-3', value: 'text-lg', label: 'text-caption' },
    md: { container: 'p-4', value: 'text-2xl', label: 'text-body-sm' },
    lg: { container: 'p-5', value: 'text-3xl', label: 'text-body-md' },
  };

  const getTrendIcon = () => {
    if (trend === 'up') {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
        </svg>
      );
    }
    if (trend === 'down') {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      );
    }
    return null;
  };

  return (
    <div
      className={`
        rounded-xl border transition-all duration-200
        ${variantStyles[variant]}
        ${sizeStyles[size].container}
        ${className}
      `}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <p className={`${sizeStyles[size].label} text-surface-500 font-medium mb-1`}>
            {label}
          </p>
          <div className="flex items-baseline gap-1">
            <span className={`${sizeStyles[size].value} font-bold tabular-nums ${valueStyles[variant]}`}>
              {value}
            </span>
            {unit && (
              <span className="text-body-sm text-surface-400 font-normal">{unit}</span>
            )}
          </div>
          {(trend || trendLabel) && (
            <div className={`flex items-center gap-1 mt-2 text-caption ${
              trend === 'up' ? 'text-red-500' : trend === 'down' ? 'text-emerald-500' : 'text-surface-500'
            }`}>
              {getTrendIcon()}
              <span>{trendLabel}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`flex-shrink-0 ${iconStyles[variant]}`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// CHART CONTAINER COMPONENT
// =============================================================================
export function ChartContainer({ children, height = 300, className = '' }) {
  return (
    <div 
      className={`relative w-full ${className}`}
      style={{ height: typeof height === 'number' ? `${height}px` : height }}
    >
      {children}
    </div>
  );
}

// =============================================================================
// CHART LEGEND COMPONENT
// =============================================================================
export function ChartLegend({ items, className = '' }) {
  return (
    <div className={`flex flex-wrap gap-4 mt-4 pt-4 border-t border-surface-100 ${className}`}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2 text-body-sm text-surface-600">
          <span
            className={`w-3 h-3 rounded-full flex-shrink-0 ${item.dashed ? 'border-2' : ''}`}
            style={{ 
              backgroundColor: item.dashed ? 'transparent' : item.color,
              borderColor: item.dashed ? item.color : 'transparent',
            }}
          />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// =============================================================================
// STATUS BADGE COMPONENT
// =============================================================================
export function StatusBadge({ status, label, size = 'md', pulse = false, className = '' }) {
  const statusStyles = {
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-red-50 text-red-700 border-red-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
    neutral: 'bg-surface-100 text-surface-600 border-surface-200',
  };

  const dotStyles = {
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
    neutral: 'bg-surface-400',
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-caption',
    md: 'px-2.5 py-1 text-body-sm',
    lg: 'px-3 py-1.5 text-body-md',
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium border
        ${statusStyles[status]}
        ${sizeStyles[size]}
        ${className}
      `}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotStyles[status]} ${pulse ? 'animate-pulse-soft' : ''}`} />
      {label}
    </span>
  );
}

// =============================================================================
// BUTTON COMPONENT
// =============================================================================
export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  icon, 
  iconPosition = 'left',
  loading = false,
  disabled = false,
  className = '',
  ...props 
}) {
  const variantStyles = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 active:bg-primary-800 focus-visible:ring-primary-500',
    secondary: 'bg-surface-100 text-surface-700 hover:bg-surface-200 active:bg-surface-300 focus-visible:ring-surface-400',
    ghost: 'bg-transparent text-surface-600 hover:bg-surface-100 active:bg-surface-200 focus-visible:ring-surface-400',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 focus-visible:ring-red-500',
  };

  const sizeStyles = {
    sm: 'px-3 py-2 text-body-sm rounded-lg gap-1.5',
    md: 'px-4 py-2.5 text-body-md rounded-xl gap-2',
    lg: 'px-6 py-3 text-body-lg rounded-2xl gap-2.5',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center font-medium
        transition-all duration-200
        focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        <>
          {icon && iconPosition === 'left' && <span className="flex-shrink-0">{icon}</span>}
          {children}
          {icon && iconPosition === 'right' && <span className="flex-shrink-0">{icon}</span>}
        </>
      )}
    </button>
  );
}

// =============================================================================
// ICON BUTTON COMPONENT
// =============================================================================
export function IconButton({ 
  children, 
  variant = 'ghost', 
  size = 'md',
  className = '',
  ...props 
}) {
  const variantStyles = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700',
    secondary: 'bg-surface-100 text-surface-600 hover:bg-surface-200',
    ghost: 'bg-transparent text-surface-500 hover:bg-surface-100 hover:text-surface-700',
  };

  const sizeStyles = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center rounded-xl
        transition-all duration-200
        focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary-500
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
}

// =============================================================================
// INPUT COMPONENT
// =============================================================================
export function Input({ 
  label, 
  prefix, 
  suffix, 
  error, 
  className = '', 
  inputClassName = '',
  size = 'md',
  ...props 
}) {
  const sizeStyles = {
    sm: 'px-3 py-2 text-body-sm rounded-lg',
    md: 'px-3.5 py-2.5 text-body-md rounded-xl',
    lg: 'px-4 py-3 text-body-lg rounded-xl',
  };

  return (
    <div className={className}>
      {label && (
        <label className="block text-body-sm font-medium text-surface-700 mb-1.5">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {prefix && (
          <span className="absolute left-3 text-surface-400 pointer-events-none">
            {prefix}
          </span>
        )}
        <input
          className={`
            w-full bg-white border border-surface-200
            text-surface-800 placeholder:text-surface-400
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
            ${error ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500' : ''}
            ${prefix ? 'pl-8' : ''}
            ${suffix ? 'pr-8' : ''}
            ${sizeStyles[size]}
            ${inputClassName}
          `}
          {...props}
        />
        {suffix && (
          <span className="absolute right-3 text-surface-400 pointer-events-none">
            {suffix}
          </span>
        )}
      </div>
      {error && (
        <p className="mt-1 text-caption text-red-500">{error}</p>
      )}
    </div>
  );
}

// =============================================================================
// SELECT COMPONENT
// =============================================================================
export function Select({ 
  label, 
  options, 
  error, 
  className = '',
  selectClassName = '',
  size = 'md',
  ...props 
}) {
  const sizeStyles = {
    sm: 'px-3 py-2 text-body-sm rounded-lg',
    md: 'px-3.5 py-2.5 text-body-md rounded-xl',
    lg: 'px-4 py-3 text-body-lg rounded-xl',
  };

  return (
    <div className={className}>
      {label && (
        <label className="block text-body-sm font-medium text-surface-700 mb-1.5">
          {label}
        </label>
      )}
      <select
        className={`
          w-full bg-white border border-surface-200
          text-surface-800 appearance-none cursor-pointer
          transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500
          bg-no-repeat bg-right
          ${error ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500' : ''}
          ${sizeStyles[size]}
          ${selectClassName}
        `}
        style={{
          backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236B7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
          backgroundPosition: 'right 0.75rem center',
          backgroundSize: '1.25rem',
          paddingRight: '2.5rem',
        }}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-caption text-red-500">{error}</p>
      )}
    </div>
  );
}

// =============================================================================
// LOADING SKELETON
// =============================================================================
export function Skeleton({ width, height, className = '', rounded = 'lg' }) {
  const roundedStyles = {
    none: '',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    xl: 'rounded-xl',
    full: 'rounded-full',
  };

  return (
    <div
      className={`bg-surface-200 animate-pulse ${roundedStyles[rounded]} ${className}`}
      style={{
        width: typeof width === 'number' ? `${width}px` : width,
        height: typeof height === 'number' ? `${height}px` : height,
      }}
    />
  );
}

// =============================================================================
// EMPTY STATE
// =============================================================================
export function EmptyState({ icon, title, description, action, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center py-12 text-center ${className}`}>
      {icon && (
        <div className="w-16 h-16 text-surface-300 mb-4">
          {icon}
        </div>
      )}
      {title && (
        <h3 className="text-heading-md text-surface-600 mb-2">{title}</h3>
      )}
      {description && (
        <p className="text-body-md text-surface-400 max-w-sm">{description}</p>
      )}
      {action && (
        <div className="mt-6">{action}</div>
      )}
    </div>
  );
}

// =============================================================================
// QUICK ACTION CARD
// =============================================================================
export function QuickAction({ icon, title, description, onClick, className = '' }) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-4 p-4 rounded-xl text-left
        bg-surface-50 border border-surface-100
        transition-all duration-200
        hover:bg-surface-100 hover:border-surface-200
        focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2
        ${className}
      `}
    >
      {icon && (
        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center">
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="text-body-md font-medium text-surface-800">{title}</div>
        {description && (
          <div className="text-body-sm text-surface-500 truncate">{description}</div>
        )}
      </div>
      <svg className="w-5 h-5 text-surface-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </button>
  );
}
