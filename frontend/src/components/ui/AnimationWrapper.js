import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Variants for common animations
const variants = {
    fadeIn: {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        exit: { opacity: 0 },
        transition: { duration: 0.3 }
    },
    slideUp: {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: -20 },
        transition: { duration: 0.4, ease: "easeOut" }
    },
    slideDown: {
        initial: { opacity: 0, y: -20 },
        animate: { opacity: 1, y: 0 },
        exit: { opacity: 0, y: 20 },
        transition: { duration: 0.4, ease: "easeOut" }
    },
    scaleIn: {
        initial: { opacity: 0, scale: 0.95 },
        animate: { opacity: 1, scale: 1 },
        exit: { opacity: 0, scale: 0.95 },
        transition: { duration: 0.2 }
    }
};

/**
 * Wrapper component to apply standard animations to children.
 * 
 * @param {Object} props
 * @param {string} props.variant - 'fadeIn', 'slideUp', 'slideDown', or 'scaleIn'
 * @param {string} props.className - Optional classes
 * @param {boolean} props.layout - Whether to animate layout changes
 * @param {React.ReactNode} props.children
 */
export function AnimationWrapper({
    children,
    variant = 'fadeIn',
    className = '',
    layout = false,
    delay = 0
}) {
    const selectedVariant = variants[variant] || variants.fadeIn;

    // Add delay to transition
    const transition = {
        ...selectedVariant.transition,
        delay
    };

    return (
        <motion.div
            initial={selectedVariant.initial}
            animate={selectedVariant.animate}
            exit={selectedVariant.exit}
            transition={transition}
            layout={layout}
            className={className}
        >
            {children}
        </motion.div>
    );
}

/**
 * Wrapper for lists to animate items presence
 */
export function AnimatedList({ children, className = '' }) {
    return (
        <AnimatePresence mode="popLayout">
            <div className={className}>
                {children}
            </div>
        </AnimatePresence>
    );
}

export default AnimationWrapper;
