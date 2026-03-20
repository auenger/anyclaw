/**
 * SkillDetail Component
 *
 * 技能详情组件：显示详细描述、参数定义、使用示例
 */

import { X, Package, Code, BookOpen, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { cn } from '../../lib/utils';
import type { Skill, SkillParameter } from '../../types';

export interface SkillDetailProps {
  skill: Skill;
  onClose?: () => void;
  onReload?: () => void;
  isReloading?: boolean;
  className?: string;
}

export function SkillDetail({
  skill,
  onClose,
  onReload,
  isReloading = false,
  className,
}: SkillDetailProps) {
  return (
    <div className={cn('p-6 space-y-6', className)}>
      {/* 头部 */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white">
            <Package className="h-7 w-7" />
          </div>
          <div>
            <h2 className="text-xl font-bold">{skill.name}</h2>
            <div className="flex items-center gap-2 mt-1">
              {skill.version && (
                <Badge variant="outline">v{skill.version}</Badge>
              )}
              {skill.author && (
                <span className="text-sm text-muted-foreground">
                  by {skill.author}
                </span>
              )}
              <Badge variant={skill.enabled ? 'success' : 'secondary'}>
                {skill.enabled ? '已启用' : '已禁用'}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onReload && (
            <Button
              variant="outline"
              size="sm"
              onClick={onReload}
              disabled={isReloading}
            >
              <RefreshCw className={cn('h-4 w-4 mr-2', isReloading && 'animate-spin')} />
              重载
            </Button>
          )}
          {onClose && (
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* 描述 */}
      <div>
        <h3 className="font-medium mb-2">描述</h3>
        <p className="text-muted-foreground">{skill.description}</p>
      </div>

      {/* 标签 */}
      {skill.tags && skill.tags.length > 0 && (
        <div>
          <h3 className="font-medium mb-2">标签</h3>
          <div className="flex flex-wrap gap-2">
            {skill.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* 参数定义 */}
      {skill.parameters && skill.parameters.length > 0 && (
        <div>
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <Code className="h-4 w-4" />
            参数
          </h3>
          <div className="space-y-3">
            {skill.parameters.map((param) => (
              <ParameterItem key={param.name} parameter={param} />
            ))}
          </div>
        </div>
      )}

      {/* 使用示例 */}
      {skill.examples && skill.examples.length > 0 && (
        <div>
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            使用示例
          </h3>
          <div className="space-y-2">
            {skill.examples.map((example, index) => (
              <Card key={index}>
                <CardContent className="p-3">
                  <code className="text-sm bg-muted p-2 rounded block overflow-x-auto">
                    {example}
                  </code>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 来源 */}
      {skill.source && (
        <div>
          <h3 className="font-medium mb-2">来源</h3>
          <p className="text-sm text-muted-foreground font-mono">{skill.source}</p>
        </div>
      )}
    </div>
  );
}

function ParameterItem({ parameter }: { parameter: SkillParameter }) {
  return (
    <div className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <code className="font-medium text-sm">{parameter.name}</code>
          <Badge variant="outline" className="text-xs">
            {parameter.type}
          </Badge>
          {parameter.required && (
            <Badge variant="destructive" className="text-xs">
              必需
            </Badge>
          )}
        </div>
        {parameter.description && (
          <p className="text-sm text-muted-foreground mt-1">
            {parameter.description}
          </p>
        )}
        {parameter.default !== undefined && (
          <p className="text-xs text-muted-foreground mt-1">
            默认值: <code>{JSON.stringify(parameter.default)}</code>
          </p>
        )}
      </div>
    </div>
  );
}

export default SkillDetail;
