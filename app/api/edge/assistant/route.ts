import { NextRequest, NextResponse } from 'next/server';

const ANTHROPIC_API_KEY = process.env.ANTHROPIC_API_KEY;

const SYSTEM_PROMPT = `You are OMI Edge's AI analyst helping users understand game analysis. You have the full pillar breakdown, edge calculations, and line movement data for the specific game being viewed.

Be concise, data-driven, and specific to THIS game. Use short paragraphs. Reference specific numbers from the game context.

Pillar scores range 0–100 (50 = neutral). Key pillars:
- Execution (20%): team performance trends
- Incentives (10%): motivation/rest factors
- Shocks (25%): injuries, weather, unexpected events
- Time Decay (10%): how stale current lines are
- Flow (25%): sharp money / public money signals
- Game Environment (10%): pace, venue, matchup dynamics

Composite score drives the OMI fair line adjustment. Edge % = gap between book line and OMI fair line.

Never recommend specific bets — explain what the data shows and let the user decide. Keep answers under 200 words unless the question requires more detail.`;

export async function POST(request: NextRequest) {
  if (!ANTHROPIC_API_KEY) {
    return NextResponse.json(
      { error: 'ANTHROPIC_API_KEY not configured' },
      { status: 500 }
    );
  }

  try {
    const { messages, gameContext } = await request.json();

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json({ error: 'Messages required' }, { status: 400 });
    }

    // Prepend game context to the first user message
    const enrichedMessages = messages.map((msg: { role: string; content: string }, i: number) => {
      if (i === 0 && msg.role === 'user' && gameContext) {
        return {
          ...msg,
          content: `[GAME CONTEXT]\n${gameContext}\n\n[USER QUESTION]\n${msg.content}`,
        };
      }
      return msg;
    });

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: SYSTEM_PROMPT,
        messages: enrichedMessages,
        stream: true,
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('[EdgeAI] Anthropic API error:', response.status, errText);
      return NextResponse.json(
        { error: `API error: ${response.status}` },
        { status: response.status }
      );
    }

    // Stream the response through
    const stream = new ReadableStream({
      async start(controller) {
        const reader = response.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.type === 'content_block_delta' && parsed.delta?.text) {
                    controller.enqueue(new TextEncoder().encode(parsed.delta.text));
                  }
                } catch {
                  // Skip unparseable chunks
                }
              }
            }
          }
        } catch (e) {
          console.error('[EdgeAI] Stream error:', e);
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
      },
    });
  } catch (e) {
    console.error('[EdgeAI] Route error:', e);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}
