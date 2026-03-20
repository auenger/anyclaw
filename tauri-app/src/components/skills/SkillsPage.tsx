/**
 * SkillsPage Component
 *
 * 技能管理页面：技能网格布局、搜索框、重载按钮
 */

import { useState } from 'react';
import { Search, RefreshCw, Package, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';
import { SkillCard } from './SkillCard';
import { SkillDetail } from './SkillDetail';
import { useSkills } from '../../hooks/useSkills';
import { cn } from '../../lib/utils';
import type { Skill } from '../../types';

export interface SkillsPageProps {
  port?: number;
  className?: string;
}

export function SkillsPage({ port, className }: SkillsPageProps) {
  const {
    filteredSkills,
    isLoading,
    isReloading,
    error,
    searchQuery,
    setSearchQuery,
    reloadSkill,
    reloadAllSkills,
  } = useSkills(port);

  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);

  const handleReloadAll = async () => {
    await reloadAllSkills();
  };

  const handleReloadSelected = async () => {
    if (selectedSkill) {
      await reloadSkill(selectedSkill.id);
    }
  };

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center h-64', className)}>
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className={cn('flex h-full', className)}>
      {/* 列表区域 */}
      <div className="flex-1 flex flex-col">
        {/* 工具栏 */}
        <div className="p-4 border-b flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索技能..."
              className="pl-10"
            />
          </div>

          <Button
            variant="outline"
            onClick={handleReloadAll}
            disabled={isReloading}
          >
            <RefreshCw className={cn('h-4 w-4 mr-2', isReloading && 'animate-spin')} />
            重载全部
          </Button>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="p-4 bg-destructive/10 text-destructive">
            {error}
          </div>
        )}

        {/* 技能网格 */}
        <ScrollArea className="flex-1">
          <div className="p-4">
            {filteredSkills.length === 0 ? (
              <div className="text-center py-12">
                <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-lg font-medium">没有找到技能</p>
                <p className="text-muted-foreground">
                  {searchQuery ? '尝试其他搜索词' : '请检查技能目录配置'}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredSkills.map((skill) => (
                  <SkillCard
                    key={skill.id}
                    skill={skill}
                    onClick={() => setSelectedSkill(skill)}
                    className={cn(
                      selectedSkill?.id === skill.id && 'ring-2 ring-primary'
                    )}
                  />
                ))}
              </div>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* 详情面板 */}
      {selectedSkill && (
        <div className="w-96 border-l bg-card overflow-y-auto">
          <SkillDetail
            skill={selectedSkill}
            onClose={() => setSelectedSkill(null)}
            onReload={handleReloadSelected}
            isReloading={isReloading}
          />
        </div>
      )}
    </div>
  );
}

export default SkillsPage;
