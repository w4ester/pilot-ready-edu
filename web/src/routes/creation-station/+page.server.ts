import type { PageServerLoad } from './$types';
import { apiServer, UnauthorizedError } from '$lib/api.server';
import { redirect } from '@sveltejs/kit';

interface RoomSummary {
  id: string;
  name: string;
  description?: string | null;
  member_count: number;
  is_archived: boolean;
  created_at?: number | null;
}

interface ToolTile {
  key: string;
  title: string;
  description: string;
  badge?: { label: string; tone: 'accent' | 'warning' | 'info' | 'neutral' };
  accent: 'indigo' | 'pink' | 'cyan' | 'teal' | 'orange' | 'blue';
  gradient: [string, string];
  icon: string;
  countValue?: number;
  countLabel?: string;
  meta?: Array<{ icon?: string; label: string }>;
  href?: string;
  disabled?: boolean;
  statusText?: string;
}

const fetchList = async <T>(event: Parameters<PageServerLoad>[0], path: string) => {
  try {
    return await apiServer.get<T[]>(event, path);
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      throw error;
    }
    console.error(`creation-station load failed for ${path}`, error);
    return [] as T[];
  }
};

export const load: PageServerLoad = async (event) => {
  const parent = await event.parent();
  if (!parent.user) {
    const next = encodeURIComponent(`${event.url.pathname}${event.url.search}`);
    throw redirect(302, `/login?next=${next}`);
  }

  let responses: [any[], any[], any[], any[], RoomSummary[]];
  try {
    responses = await Promise.all([
      fetchList<any>(event, '/api/v1/prompts'),
      fetchList<any>(event, '/api/v1/tools'),
      fetchList<any>(event, '/api/v1/models'),
      fetchList<any>(event, '/api/v1/libraries'),
      fetchList<RoomSummary>(event, '/api/v1/rooms'),
    ]);
  } catch (error) {
    if (error instanceof UnauthorizedError) {
      const next = encodeURIComponent(`${event.url.pathname}${event.url.search}`);
      throw redirect(302, `/login?next=${next}`);
    }
    throw error;
  }

  const [prompts, tools, models, libraries, rooms] = responses;

  const totalResources = prompts.length + tools.length + models.length + libraries.length;
  const activeClasses = rooms.filter((room) => !room.is_archived).length;
  const studentsReached = rooms.reduce((acc, room) => acc + (room.member_count ?? 0), 0);

  const formatter = new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  });

  const stats = [
    { label: 'Resources Created', value: totalResources, display: formatter.format(totalResources), icon: '🧠' },
    { label: 'Active Classes', value: activeClasses, display: formatter.format(activeClasses), icon: '🏫' },
    { label: 'Students Reached', value: studentsReached, display: formatter.format(studentsReached), icon: '🎓' },
  ];

  const tiles: ToolTile[] = [
    {
      key: 'prompts',
      title: 'Prompts',
      description: 'Create reusable AI prompts with slash commands for instant access across chats.',
      badge: { label: 'Popular', tone: 'accent' },
      accent: 'indigo',
      gradient: ['#6c5cff', '#2a1e80'],
      icon: '✏️',
      countValue: prompts.length,
      countLabel: 'created',
      meta: [{ icon: '⚡', label: '/commands ready' }],
      disabled: false,
      href: '/creation-station/prompts'
    },
    {
      key: 'tools',
      title: 'Tools',
      description: 'Build Python functions to extend AI capabilities with custom logic and integrations.',
      badge: { label: 'Advanced', tone: 'info' },
      accent: 'pink',
      gradient: ['#ff6f9f', '#3c1035'],
      icon: '🧰',
      countValue: tools.length,
      countLabel: tools.length === 1 ? 'tool' : 'tools',
      meta: [{ icon: '🛠️', label: 'Tested' }],
      href: '/creation-station/tools'
    },
    {
      key: 'models',
      title: 'Models',
      description: 'Configure AI models with custom personas, parameters, and attached tools.',
      badge: { label: 'Essential', tone: 'neutral' },
      accent: 'cyan',
      gradient: ['#4ac7ff', '#102c46'],
      icon: '🤖',
      countValue: models.length,
      countLabel: models.length === 1 ? 'model' : 'models',
      meta: [{ icon: '🤖', label: 'Custom AI ready' }],
      disabled: true,
      statusText: 'Coming Soon'
    },
    {
      key: 'libraries',
      title: 'Libraries',
      description: 'Build RAG knowledge bases from documents for contextual AI responses.',
      badge: { label: 'Knowledge', tone: 'info' },
      accent: 'teal',
      gradient: ['#37f0c2', '#0a3e2f'],
      icon: '📚',
      countValue: libraries.length,
      countLabel: libraries.length === 1 ? 'library' : 'libraries',
      meta: [{ icon: '📦', label: 'Document syncing' }],
      disabled: false,
      href: '/creation-station/libraries'
    },
    {
      key: 'cards',
      title: 'Cards',
      description: 'Generate adaptive micro-lessons that adjust to student levels automatically.',
      badge: { label: 'New', tone: 'accent' },
      accent: 'orange',
      gradient: ['#ffb457', '#3a2004'],
      icon: '🃏',
      meta: [{ icon: '⚡', label: 'Automations in progress' }],
      disabled: true,
      statusText: 'In Design'
    },
    {
      key: 'rooms',
      title: 'Rooms',
      description: 'Configure collaborative spaces to plan and share resources.',
      badge: { label: 'Collaborative', tone: 'neutral' },
      accent: 'blue',
      gradient: ['#6f8cff', '#14204b'],
      icon: '💬',
      meta: [{ icon: '🛡️', label: 'Safe mode' }],
      disabled: false,
      href: '/creation-station/rooms'
    }
  ];

  return {
    stats,
    tiles,
  };
};
