/**
 * SkillCard Component
 *
 * 技能卡片组件：显示技能图标、名称、描述、状态
 */

import { Package } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import type { Skill } from '../../types';

export interface SkillCardProps {
  skill: Skill;
  onClick?: () => void;
  className?: string;
}

export function SkillCard({ skill, onClick, className }: SkillCardProps) {
  const statusColor = skill.enabled
    ? 'bg-green-500'
    : 'bg-gray-400';

  const statusText = skill.enabled ? '已启用' : '已禁用';

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:shadow-md hover:border-primary/50',
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white">
              <Package className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base">{skill.name}</CardTitle>
              {skill.version && (
                <span className="text-xs text-muted-foreground">v{skill.version}</span>
              )}
            </div>
          </div>
          <div className={cn('h-2 w-2 rounded-full', statusColor)} title={statusText} />
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="line-clamp-2">
          {skill.description}
        </CardDescription>

        {skill.tags && skill.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {skill.tags.slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
            {skill.tags.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{skill.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default SkillCard;
