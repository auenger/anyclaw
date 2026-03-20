/**
 * InputArea Component
 *
 * 聊天输入区域，支持发送和停止功能
 */

import { useState, useCallback } from 'react';
import { Send, Square } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { cn } from '../../lib/utils';

export interface InputAreaProps {
  onSend: (message: string) => void;
  onStop?: () => void;
  disabled?: boolean;
  isStreaming?: boolean;
  isLoading?: boolean;
  placeholder?: string;
  className?: string;
}

export function InputArea({
  onSend,
  onStop,
  disabled = false,
  isStreaming = false,
  isLoading = false,
  placeholder = '输入消息...',
  className,
}: InputAreaProps) {
  const [input, setInput] = useState('');

  const handleSend = useCallback(() => {
    if (!input.trim() || disabled || isLoading) return;

    onSend(input.trim());
    setInput('');
  }, [input, disabled, isLoading, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  const canSend = !disabled && !isLoading && input.trim().length > 0;

  return (
    <div className={cn('border-t p-4', className)}>
      <div className="max-w-3xl mx-auto flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          className="flex-1"
        />

        {isStreaming ? (
          <Button
            variant="destructive"
            onClick={onStop}
            disabled={!onStop}
            title="停止生成"
          >
            <Square className="h-4 w-4" />
          </Button>
        ) : (
          <Button onClick={handleSend} disabled={!canSend}>
            <Send className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}

export default InputArea;
