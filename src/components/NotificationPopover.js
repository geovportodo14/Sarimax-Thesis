import React from 'react';
import { Card } from './ui/index';
import { Bell, AlertTriangle, TrendingDown, CheckCircle2, X } from 'lucide-react';

const NotificationPopover = ({ isOpen, onClose, notifications = [] }) => {
    if (!isOpen) return null;

    return (
        <>
            {/* 🛡️ THE FIX 1: Invisible Full-Screen Backdrop! 
                If the user clicks anywhere outside the popover, this catches it and closes the menu. */}
            <div
                className="fixed inset-0 z-[90]"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* 📱 THE FIX 2: Safer Mobile Positioning
                Removed the negative right margins and used max-w to ensure it NEVER causes a horizontal scrollbar. */}
            <div className="absolute right-0 mt-3 w-[calc(100vw-2rem)] max-w-[360px] sm:max-w-none sm:w-96 z-[100] animate-in fade-in slide-in-from-top-2 duration-200 origin-top-right">
                <Card className="shadow-2xl border-surface-100 overflow-hidden ring-1 ring-black/5">
                    <div className="p-4 border-b border-surface-50 flex items-center justify-between bg-surface-50">
                        <div className="flex items-center gap-2">
                            <Bell size={18} className="text-primary-500" />
                            <h3 className="font-bold text-surface-900 text-body-md">Notifications</h3>
                            {notifications.length > 0 && (
                                <span className="bg-primary-500 text-white text-[10px] px-1.5 py-0.5 rounded-full shadow-sm">
                                    {notifications.length}
                                </span>
                            )}
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1.5 hover:bg-surface-200 rounded-lg transition-colors text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-100"
                        >
                            <X size={16} />
                        </button>
                    </div>

                    <div className="max-h-[400px] overflow-y-auto overscroll-contain relative z-[101]">
                        {notifications.length === 0 ? (
                            <div className="p-8 text-center">
                                <div className="w-12 h-12 bg-surface-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                    <CheckCircle2 size={24} className="text-surface-400" />
                                </div>
                                <p className="text-surface-500 text-body-sm">All caught up! No new alerts.</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-surface-50">
                                {notifications.map((notif) => (
                                    <div
                                        key={notif.id}
                                        className={`p-4 hover:bg-surface-50 transition-colors cursor-pointer group ${notif.priority === 'high' ? 'bg-red-50/30' : ''
                                            }`}
                                    >
                                        <div className="flex gap-3">
                                            <div className={`mt-1 flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${notif.type === 'at-risk' ? 'bg-red-100 text-red-600' :
                                                notif.type === 'approaching' ? 'bg-amber-100 text-amber-600' :
                                                    'bg-sky-100 text-sky-600'
                                                }`}>
                                                {notif.type === 'at-risk' ? <AlertTriangle size={16} /> :
                                                    notif.type === 'approaching' ? <AlertTriangle size={16} /> :
                                                        <TrendingDown size={16} />}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center justify-between mb-0.5">
                                                    <p className={`text-body-sm font-semibold truncate pr-2 ${notif.priority === 'high' ? 'text-red-700' : 'text-surface-900'
                                                        }`}>
                                                        {notif.title}
                                                    </p>
                                                    <span className="text-[10px] font-medium text-surface-400 whitespace-nowrap">
                                                        {notif.time}
                                                    </span>
                                                </div>
                                                <p className="text-body-xs text-surface-500 leading-relaxed mb-2">
                                                    {notif.message}
                                                </p>
                                                {notif.action && (
                                                    <button className="text-primary-600 text-[11px] font-bold hover:text-primary-700 transition-colors">
                                                        {notif.action}
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {notifications.length > 0 && (
                        <div className="p-3 border-t border-surface-50 text-center bg-surface-50 relative z-[101]">
                            <button className="text-body-xs font-semibold text-surface-500 hover:text-primary-600 transition-colors">
                                Mark all as read
                            </button>
                        </div>
                    )}
                </Card>
            </div>
        </>
    );
};

export default NotificationPopover;