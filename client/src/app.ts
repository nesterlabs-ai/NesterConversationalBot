/**
 * Copyright (c) 2024–2025, Daily
 *
 * SPDX-License-Identifier: BSD 2-Clause License
 */

/**
 * RTVI Client Implementation
 *
 * This client connects to an RTVI-compatible bot server using WebSocket.
 *
 * Requirements:
 * - A running RTVI bot server (defaults to http://localhost:7860)
 */

import {
  RTVIClient,
  RTVIClientOptions,
  RTVIEvent,
} from '@pipecat-ai/client-js';
import {
  WebSocketTransport
} from "@pipecat-ai/websocket-transport";

class WebsocketClientApp {
  private rtviClient: RTVIClient | null = null;
  private connectBtn: HTMLButtonElement | null = null;
  private statusDot: HTMLElement | null = null;
  private debugLog: HTMLElement | null = null;
  private voiceOverlay: HTMLElement | null = null;
  private overlayWaveContainer: HTMLElement | null = null;
  private logToggle: HTMLElement | null = null;
  private botAudio: HTMLAudioElement;
  private isConnected: boolean = false;

  constructor() {
    console.log("Voice Chat Initializing...");
    this.botAudio = document.createElement('audio');
    this.botAudio.autoplay = true;
    document.body.appendChild(this.botAudio);

    this.setupDOMElements();
    this.setupEventListeners();
    this.initializeVisualEffects();
  }

  /**
   * Set up references to DOM elements and create necessary media elements
   */
  private setupDOMElements(): void {
    this.connectBtn = document.getElementById('connect-btn') as HTMLButtonElement;
    this.statusDot = document.getElementById('status-dot');
    this.debugLog = document.getElementById('debug-log');
    this.voiceOverlay = document.getElementById('voice-overlay');
    this.overlayWaveContainer = document.querySelector('.overlay-wave-container') as HTMLElement;
    this.logToggle = document.getElementById('log-toggle');
  }

  /**
   * Set up event listeners for interactive elements
   */
  private setupEventListeners(): void {
    this.connectBtn?.addEventListener('click', () => this.toggleConnection());
    this.logToggle?.addEventListener('click', () => this.toggleLog());
  }

  /**
   * Initialize visual effects and animations
   */
  private initializeVisualEffects(): void {
    this.updateConnectionVisuals(false);
  }

  /**
   * Toggle connection state
   */
  private async toggleConnection(): Promise<void> {
    if (this.isConnected) {
      await this.disconnect();
    } else {
      await this.connect();
    }
  }

  /**
   * Toggle log panel visibility
   */
  private toggleLog(): void {
    if (this.debugLog) {
      this.debugLog.classList.toggle('collapsed');
    }
  }

  /**
   * Update visual elements based on connection state
   */
  private updateConnectionVisuals(connected: boolean): void {
    this.isConnected = connected;
    
    if (this.statusDot) {
      if (connected) {
        this.statusDot.classList.add('connected');
      } else {
        this.statusDot.classList.remove('connected');
      }
    }

    if (this.connectBtn) {
      if (connected) {
        this.connectBtn.classList.add('connected');
        this.connectBtn.disabled = false;
      } else {
        this.connectBtn.classList.remove('connected');
        this.connectBtn.disabled = false;
      }
    }


    if (this.voiceOverlay) {
      if (connected) {
        this.voiceOverlay.classList.add('active');
      } else {
        this.voiceOverlay.classList.remove('active');
      }
    }

    if (this.overlayWaveContainer) {
      if (connected) {
        this.overlayWaveContainer.classList.add('active');
      } else {
        this.overlayWaveContainer.classList.remove('active');
      }
    }
  }

  /**
   * Add a timestamped message to the debug log
   */
  private log(message: string): void {
    if (!this.debugLog) return;
    const entry = document.createElement('div');
    entry.textContent = `${new Date().toISOString()} - ${message}`;
    if (message.startsWith('User: ')) {
      entry.style.color = '#2196F3';
    } else if (message.startsWith('Bot: ')) {
      entry.style.color = '#4CAF50';
    }
    this.debugLog.appendChild(entry);
    this.debugLog.scrollTop = this.debugLog.scrollHeight;
    console.log(message);
  }

  /**
   * Update the connection status display
   */
  private updateStatus(status: string): void {
    const isConnected = status === 'Connected' || status === 'Online';
    this.updateConnectionVisuals(isConnected);
    this.log(`Connection Status: ${status}`);
  }

  /**
   * Check for available media tracks and set them up if present
   * This is called when the bot is ready or when the transport state changes to ready
   */
  setupMediaTracks() {
    if (!this.rtviClient) return;
    const tracks = this.rtviClient.tracks();
    if (tracks.bot?.audio) {
      this.setupAudioTrack(tracks.bot.audio);
    }
  }

  /**
   * Set up listeners for track events (start/stop)
   * This handles new tracks being added during the session
   */
  setupTrackListeners() {
    if (!this.rtviClient) return;

    // Listen for new tracks starting
    this.rtviClient.on(RTVIEvent.TrackStarted, (track, participant) => {
      // Only handle non-local (bot) tracks
      if (!participant?.local && track.kind === 'audio') {
        this.setupAudioTrack(track);
      }
    });

    // Listen for tracks stopping
    this.rtviClient.on(RTVIEvent.TrackStopped, (track, participant) => {
      this.log(`Track stopped: ${track.kind} from ${participant?.name || 'unknown'}`);
    });
  }

  /**
   * Set up an audio track for playback
   * Handles both initial setup and track updates
   */
  private setupAudioTrack(track: MediaStreamTrack): void {
    this.log('Setting up audio track');
    if (this.botAudio.srcObject && "getAudioTracks" in this.botAudio.srcObject) {
      const oldTrack = this.botAudio.srcObject.getAudioTracks()[0];
      if (oldTrack?.id === track.id) return;
    }
    this.botAudio.srcObject = new MediaStream([track]);
  }

  /**
   * Initialize and connect to the bot
   * This sets up the RTVI client, initializes devices, and establishes the connection
   */
  public async connect(): Promise<void> {
    try {
      const startTime = Date.now();

      //const transport = new DailyTransport();
      const transport = new WebSocketTransport();
      const RTVIConfig: RTVIClientOptions = {
        transport,
        params: {
          // The baseURL and endpoint of your bot server that the client will connect to
          baseUrl: 'http://localhost:7860',
          endpoints: { connect: '/connect' },
        },
        enableMic: true,
        enableCam: false,
        callbacks: {
          onConnected: () => {
            this.updateStatus('Connected');
            this.log('Connection established successfully');
          },
          onDisconnected: () => {
            this.updateStatus('Disconnected');
            this.log('Connection terminated');
          },
          onBotReady: (data) => {
            this.log(`Bot ready: ${JSON.stringify(data)}`);
            this.setupMediaTracks();
          },
          onUserTranscript: (data) => {
            if (data.final) {
              this.log(`You: ${data.text}`);
            }
          },
          onBotTranscript: (data) => this.log(`Bot: ${data.text}`),
          onMessageError: (error) => console.error('Message error:', error),
          onError: (error) => console.error('Error:', error),
        },
      }
      this.rtviClient = new RTVIClient(RTVIConfig);
      this.setupTrackListeners();

      this.log('Initializing devices...');
      await this.rtviClient.initDevices();

      this.log('Connecting to server...');
      await this.rtviClient.connect();

      const timeTaken = Date.now() - startTime;
      this.log(`Connection established in ${timeTaken}ms`);
    } catch (error) {
      this.log(`Connection failed: ${(error as Error).message}`);
      this.updateStatus('Error');
      if (this.rtviClient) {
        try {
          await this.rtviClient.disconnect();
        } catch (disconnectError) {
          this.log(`Cleanup error: ${disconnectError}`);
        }
      }
    }
  }

  /**
   * Disconnect from the bot and clean up media resources
   */
  public async disconnect(): Promise<void> {
    if (this.rtviClient) {
      try {
        this.log('Disconnecting...');
        await this.rtviClient.disconnect();
        this.rtviClient = null;
        if (this.botAudio.srcObject && "getAudioTracks" in this.botAudio.srcObject) {
          this.botAudio.srcObject.getAudioTracks().forEach((track) => track.stop());
          this.botAudio.srcObject = null;
        }
        this.log('Disconnected successfully');
      } catch (error) {
        this.log(`Disconnect error: ${(error as Error).message}`);
      }
    }
  }

}

declare global {
  interface Window {
    WebsocketClientApp: typeof WebsocketClientApp;
  }
}

window.addEventListener('DOMContentLoaded', () => {
  window.WebsocketClientApp = WebsocketClientApp;
  new WebsocketClientApp();
});
