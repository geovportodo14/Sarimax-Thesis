import React from 'react';
import { Card } from './ui/index';
import { Bell, AlertTriangle, TrendingDown, CheckCircle2, X } from 'lucide-react';

const NotificationPopover = ({ isOpen, onClose, notifications = [] }) => {
    if (!isOpen) return null;

    return (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
            <Card className="shadow-2xl border-surface-100 overflow-hidden">
                <div className="p-4 border-b border-surface-50 flex items-center justify-between bg-surface-50/50">
                    <div className="flex items-center gap-2">
                        <Bell size={18} className="text-primary-500" />
                        <h3 className="font-bold text-surface-900 text-body-md">Notifications</h3>
                        {notifications.length > 0 && (
                            <span className="bg-primary-500 text-white text-[10px] px-1.5 py-0.5 rounded-full">
                                {notifications.length}
                            </span>
                        )}
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-surface-200 rounded-lg transition-colors text-surface-400"
                    >
                        <X size={16} />
                    </button>
                </div>

                <div className="max-h-[400px] overflow-y-auto">
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
                                                <p className={`text-body-sm font-semibold truncate ${notif.priority === 'high' ? 'text-red-700' : 'text-surface-900'
                                                    }`}>
                                                    {notif.title}
                                                </p>
                                                <span className="text-[10px] text-surface-400 whitespace-nowrap ml-2">
                                                    {notif.time}
                                                </span>
                                            </div>
                                            <p className="text-body-xs text-surface-500 leading-relaxed mb-2">
                                                {notif.message}
                                            </p>
                                            {notif.action && (
                                                <button className="text-primary-600 text-[11px] font-bold hover:underline">
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
                    <div className="p-3 border-t border-surface-50 text-center">
                        <button className="text-body-xs font-semibold text-surface-500 hover:text-primary-600 transition-colors">
                            Mark all as read
                        </button>
                    </div>
                )}
            </Card>

            {/* Invisible backdrop for closing when clicking outside is usually handled by a wrapper, 
          but for simplicity we'll let the header control state */}
        </div>
    );
};

export default NotificationPopover;
