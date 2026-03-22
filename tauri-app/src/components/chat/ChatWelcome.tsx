import { useMemo } from "react";
import { cn } from "@/lib/utils";
import { useI18n } from "@/i18n";
import beeImage from "@/assets/bee.png";

// 随机欢迎语 - 中文
const GREETINGS_ZH = [
  "有什么我可以帮你的吗？",
  "今天想做点什么呢？",
  "准备好一起探索了吗？",
  "让我来帮你解决问题吧！",
  "有什么有趣的想法想聊聊？",
  "我在这里等你很久了～",
  "来吧，让我们开始这段旅程！",
];

// 随机欢迎语 - 英文
const GREETINGS_EN = [
  "What can I help you with today?",
  "Ready to explore together?",
  "Let me help you solve problems!",
  "Any interesting ideas to discuss?",
  "I've been waiting for you!",
  "Let's start this journey!",
];

interface ChatWelcomeProps {
  className?: string;
}

export function ChatWelcome({ className }: ChatWelcomeProps) {
  const { t, locale } = useI18n();

  // 根据语言选择欢迎语数组
  const greetings = locale === 'zh' ? GREETINGS_ZH : GREETINGS_EN;

  // 随机选择一个欢迎语
  const greeting = useMemo(() => {
    return greetings[Math.floor(Math.random() * greetings.length)];
  }, [greetings]);

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center h-full text-center px-4",
        className
      )}
    >
      {/* Logo */}
      <img
        src={beeImage}
        alt="AnyClaw"
        className="w-24 h-24 mb-6 object-contain transition-transform duration-300 ease-out hover:scale-110 hover:rotate-3"
      />

      {/* Welcome text */}
      <h1 className="text-2xl font-semibold mb-2">
        {t.chat.welcome}
      </h1>
      <p className="text-muted-foreground text-sm max-w-md mb-8">
        {greeting}
      </p>
    </div>
  );
}
