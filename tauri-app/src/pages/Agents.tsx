/**
 * Agents Page
 *
 * Agent 管理页面，使用真实 API
 */

import { useState } from 'react';
import { Plus, AlertCircle } from 'lucide-react';
import { SidePanel } from '@/components/layout/SidePanel';
import { AgentList, AgentDetail, CreateAgentDialog, EditAgentDialog } from '@/components/agents';
import { useAgents } from '@/hooks';
import { useI18n } from '@/i18n';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type { Agent, CreateAgentRequest, UpdateAgentRequest } from '@/types';

export function Agents() {
  const { t } = useI18n();
  const {
    agents,
    isLoading,
    error,
    createAgent,
    updateAgent,
    deleteAgent,
    activateAgent,
    deactivateAgent,
  } = useAgents();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<Agent | null>(null);

  const selectedAgent = agents.find((a) => a.id === selectedId) || null;

  // 创建 Agent
  const handleCreate = async (data: CreateAgentRequest): Promise<Agent | null> => {
    const result = await createAgent(data);
    if (result) {
      setSelectedId(result.id);
    }
    return result;
  };

  // 更新 Agent
  const handleUpdate = async (id: string, data: UpdateAgentRequest): Promise<Agent | null> => {
    return updateAgent(id, data);
  };

  // 删除确认
  const handleDeleteClick = () => {
    if (selectedAgent && selectedAgent.id !== 'default') {
      setAgentToDelete(selectedAgent);
      setShowDeleteConfirm(true);
    }
  };

  // 确认删除
  const handleDeleteConfirm = async () => {
    if (agentToDelete) {
      const success = await deleteAgent(agentToDelete.id);
      if (success) {
        setSelectedId(null);
        setShowDeleteConfirm(false);
        setAgentToDelete(null);
      }
    }
  };

  // 激活 Agent
  const handleActivate = async () => {
    if (selectedAgent) {
      await activateAgent(selectedAgent.id);
    }
  };

  // 禁用 Agent
  const handleDeactivate = async () => {
    if (selectedAgent) {
      await deactivateAgent(selectedAgent.id);
    }
  };

  return (
    <div className="h-full flex">
      {/* Left Panel: Agent List */}
      <SidePanel>
        <div className="p-4 border-b border-[var(--subtle-border)]">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium">{t.agents.title}</h2>
            <button
              onClick={() => setShowCreateDialog(true)}
              className="p-1.5 rounded-lg hover:bg-accent text-muted-foreground hover:text-foreground"
              title={t.agents.createAgent}
            >
              <Plus size={16} />
            </button>
          </div>
        </div>

        <AgentList
          agents={agents}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />

        {/* Error Display */}
        {error && (
          <div className="p-2 border-t border-[var(--subtle-border)]">
            <div className="flex items-center gap-2 text-sm text-red-500">
              <AlertCircle size={14} />
              <span className="truncate">{error}</span>
            </div>
          </div>
        )}
      </SidePanel>

      {/* Right Panel: Agent Details */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <AgentDetail
          agent={selectedAgent}
          isLoading={isLoading}
          onEdit={() => setShowEditDialog(true)}
          onDelete={handleDeleteClick}
          onActivate={handleActivate}
          onDeactivate={handleDeactivate}
        />
      </div>

      {/* Create Dialog */}
      <CreateAgentDialog
        isOpen={showCreateDialog}
        onClose={() => setShowCreateDialog(false)}
        onCreate={handleCreate}
      />

      {/* Edit Dialog */}
      <EditAgentDialog
        isOpen={showEditDialog}
        agent={selectedAgent}
        onClose={() => setShowEditDialog(false)}
        onUpdate={handleUpdate}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteConfirm} onOpenChange={setShowDeleteConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{t.agents.deleteAgent}</AlertDialogTitle>
            <AlertDialogDescription>
              {t.agents.confirmDelete}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>{t.common.cancel}</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-500 hover:bg-red-600"
            >
              {t.common.delete}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
