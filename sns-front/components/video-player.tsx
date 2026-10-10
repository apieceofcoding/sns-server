"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import {
  Play,
  Pause,
  Volume2,
  VolumeX,
  Volume1,
  Maximize,
  Minimize,
  RotateCcw
} from "lucide-react"
import { cn } from "@/lib/utils"

interface VideoPlayerProps {
  src: string
  className?: string
  autoPlay?: boolean
  muted?: boolean
  loop?: boolean
  isGif?: boolean
  autoPlayOnView?: boolean // 뷰포트에 들어오면 자동재생
}

export function VideoPlayer({
  src,
  className,
  autoPlay = true,
  muted: initialMuted = true,
  loop = true,
  isGif = false,
  autoPlayOnView = false
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const progressRef = useRef<HTMLDivElement>(null)
  const volumeRef = useRef<HTMLDivElement>(null)
  const hideControlsTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [isMuted, setIsMuted] = useState(initialMuted)
  const [volume, setVolume] = useState(initialMuted ? 0 : 1)
  const [previousVolume, setPreviousVolume] = useState(1)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [progress, setProgress] = useState(0)
  const [buffered, setBuffered] = useState(0)
  const [showControls, setShowControls] = useState(true)
  const [showVolumeSlider, setShowVolumeSlider] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isEnded, setIsEnded] = useState(false)
  const [isHovering, setIsHovering] = useState(false)

  // 컨트롤 숨기기 타이머
  const resetHideControlsTimer = useCallback(() => {
    if (hideControlsTimeoutRef.current) {
      clearTimeout(hideControlsTimeoutRef.current)
    }
    setShowControls(true)
    if (isPlaying && !isHovering) {
      hideControlsTimeoutRef.current = setTimeout(() => {
        setShowControls(false)
      }, 2500)
    }
  }, [isPlaying, isHovering])

  useEffect(() => {
    resetHideControlsTimer()
    return () => {
      if (hideControlsTimeoutRef.current) {
        clearTimeout(hideControlsTimeoutRef.current)
      }
    }
  }, [isPlaying, resetHideControlsTimer])

  // 비디오 이벤트 핸들러
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime)
      setProgress((video.currentTime / video.duration) * 100)
    }

    const handleLoadedMetadata = () => {
      setDuration(video.duration)
    }

    const handleProgress = () => {
      if (video.buffered.length > 0) {
        const bufferedEnd = video.buffered.end(video.buffered.length - 1)
        setBuffered((bufferedEnd / video.duration) * 100)
      }
    }

    const handleEnded = () => {
      setIsEnded(true)
      setIsPlaying(false)
      setShowControls(true)
    }

    const handlePlay = () => {
      setIsPlaying(true)
      setIsEnded(false)
    }

    const handlePause = () => {
      setIsPlaying(false)
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('progress', handleProgress)
    video.addEventListener('ended', handleEnded)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      video.removeEventListener('progress', handleProgress)
      video.removeEventListener('ended', handleEnded)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
    }
  }, [])

  // 전체화면 변경 감지
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement)
    }

    document.addEventListener('fullscreenchange', handleFullscreenChange)
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
    }
  }, [])

  // 뷰포트 진입 시 자동재생
  useEffect(() => {
    if (!autoPlayOnView) return

    const video = videoRef.current
    const container = containerRef.current
    if (!video || !container) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // 뷰포트에 50% 이상 보이면 재생
            video.play().catch(() => {
              // 자동재생 실패 시 무시 (브라우저 정책)
            })
          } else {
            // 뷰포트를 벗어나면 일시정지
            video.pause()
          }
        })
      },
      {
        threshold: 0.5, // 50% 이상 보일 때
      }
    )

    observer.observe(container)

    return () => {
      observer.disconnect()
    }
  }, [autoPlayOnView])

  const togglePlay = (e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    if (!video) return

    if (isEnded) {
      video.currentTime = 0
      video.play()
      setIsEnded(false)
    } else if (video.paused) {
      video.play()
    } else {
      video.pause()
    }
  }

  const toggleMute = (e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    if (!video) return

    if (isMuted || volume === 0) {
      // 음소거 해제
      const newVolume = previousVolume > 0 ? previousVolume : 1
      video.volume = newVolume
      video.muted = false
      setVolume(newVolume)
      setIsMuted(false)
    } else {
      // 음소거
      setPreviousVolume(volume)
      video.muted = true
      setIsMuted(true)
    }
  }

  const handleVolumeChange = (e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    const volumeBar = volumeRef.current
    if (!video || !volumeBar) return

    const rect = volumeBar.getBoundingClientRect()
    const clickY = rect.bottom - e.clientY
    const percentage = Math.max(0, Math.min(1, clickY / rect.height))

    video.volume = percentage
    video.muted = percentage === 0
    setVolume(percentage)
    setIsMuted(percentage === 0)
    if (percentage > 0) {
      setPreviousVolume(percentage)
    }
  }

  const handleVolumeDrag = (e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()

    const video = videoRef.current
    const volumeBar = volumeRef.current
    if (!video || !volumeBar) return

    const updateVolume = (clientY: number) => {
      const rect = volumeBar.getBoundingClientRect()
      const clickY = rect.bottom - clientY
      const percentage = Math.max(0, Math.min(1, clickY / rect.height))

      video.volume = percentage
      video.muted = percentage === 0
      setVolume(percentage)
      setIsMuted(percentage === 0)
      if (percentage > 0) {
        setPreviousVolume(percentage)
      }
    }

    const handleMouseMove = (e: MouseEvent) => {
      updateVolume(e.clientY)
    }

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  const getVolumeIcon = () => {
    if (isMuted || volume === 0) {
      return <VolumeX className="w-5 h-5 text-white" />
    } else if (volume < 0.5) {
      return <Volume1 className="w-5 h-5 text-white" />
    } else {
      return <Volume2 className="w-5 h-5 text-white" />
    }
  }

  const toggleFullscreen = async (e: React.MouseEvent) => {
    e.stopPropagation()
    const container = containerRef.current
    if (!container) return

    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen()
      } else {
        await container.requestFullscreen()
      }
    } catch (err) {
      console.error('Fullscreen error:', err)
    }
  }

  const handleProgressClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    const progressBar = progressRef.current
    if (!video || !progressBar) return

    const rect = progressBar.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const percentage = clickX / rect.width
    video.currentTime = percentage * video.duration
  }

  const handleContainerClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    togglePlay(e)
  }

  const handleMouseMove = () => {
    resetHideControlsTimer()
  }

  const formatTime = (time: number) => {
    if (isNaN(time)) return "0:00"
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative bg-black group cursor-pointer overflow-hidden",
        isFullscreen && "w-screen h-screen",
        className
      )}
      onClick={handleContainerClick}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => {
        setIsHovering(true)
        setShowControls(true)
      }}
      onMouseLeave={() => {
        setIsHovering(false)
        if (isPlaying) {
          hideControlsTimeoutRef.current = setTimeout(() => {
            setShowControls(false)
          }, 1000)
        }
      }}
    >
      <video
        ref={videoRef}
        src={src}
        className="w-full h-full object-contain"
        autoPlay={autoPlay}
        muted={initialMuted}
        loop={loop}
        playsInline
        preload="metadata"
      />

      {/* 중앙 재생/일시정지 버튼 */}
      <div
        className={cn(
          "absolute inset-0 flex items-center justify-center transition-opacity duration-200",
          (isPlaying && !showControls) ? "opacity-0" : "opacity-100"
        )}
      >
        {(!isPlaying || isEnded) && (
          <button
            onClick={togglePlay}
            className="w-16 h-16 rounded-full bg-primary/90 hover:bg-primary flex items-center justify-center transition-all hover:scale-110"
          >
            {isEnded ? (
              <RotateCcw className="w-8 h-8 text-primary-foreground" />
            ) : (
              <Play className="w-8 h-8 text-primary-foreground ml-1" />
            )}
          </button>
        )}
      </div>

      {/* 하단 컨트롤 바 */}
      <div
        className={cn(
          "absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent transition-opacity duration-200 pt-8 pb-2 px-3",
          showControls ? "opacity-100" : "opacity-0"
        )}
      >
        {/* 프로그레스 바 */}
        <div
          ref={progressRef}
          className="h-1 bg-white/30 rounded-full cursor-pointer mb-2 group/progress"
          onClick={handleProgressClick}
        >
          {/* 버퍼 프로그레스 */}
          <div
            className="absolute h-1 bg-white/50 rounded-full pointer-events-none"
            style={{ width: `${buffered}%` }}
          />
          {/* 재생 프로그레스 */}
          <div
            className="h-1 bg-primary rounded-full relative"
            style={{ width: `${progress}%` }}
          >
            {/* 드래그 핸들 */}
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-primary rounded-full opacity-0 group-hover/progress:opacity-100 transition-opacity" />
          </div>
        </div>

        {/* 컨트롤 버튼들 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* 재생/일시정지 */}
            <button
              onClick={togglePlay}
              className="p-1.5 hover:bg-white/20 rounded-full transition-colors"
            >
              {isPlaying ? (
                <Pause className="w-5 h-5 text-white" />
              ) : (
                <Play className="w-5 h-5 text-white" />
              )}
            </button>

            {/* 시간 표시 */}
            <span className="text-white text-xs font-medium tabular-nums">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <div className="flex items-center gap-1">
            {/* 볼륨 컨트롤 */}
            <div
              className="relative"
              onMouseEnter={() => setShowVolumeSlider(true)}
              onMouseLeave={() => setShowVolumeSlider(false)}
            >
              {/* 볼륨 슬라이더 (호버 시 표시) */}
              <div
                className={cn(
                  "absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-3 bg-black/90 rounded-lg transition-all duration-200",
                  showVolumeSlider ? "opacity-100 visible" : "opacity-0 invisible"
                )}
                onClick={(e) => e.stopPropagation()}
              >
                <div
                  ref={volumeRef}
                  className="w-1 h-20 bg-white/30 rounded-full cursor-pointer relative"
                  onClick={handleVolumeChange}
                  onMouseDown={handleVolumeDrag}
                >
                  {/* 볼륨 레벨 */}
                  <div
                    className="absolute bottom-0 left-0 right-0 bg-primary rounded-full"
                    style={{ height: `${(isMuted ? 0 : volume) * 100}%` }}
                  />
                  {/* 드래그 핸들 */}
                  <div
                    className="absolute left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-md"
                    style={{ bottom: `calc(${(isMuted ? 0 : volume) * 100}% - 6px)` }}
                  />
                </div>
              </div>

              {/* 음소거/볼륨 버튼 */}
              <button
                onClick={toggleMute}
                className="p-1.5 hover:bg-white/20 rounded-full transition-colors"
              >
                {getVolumeIcon()}
              </button>
            </div>

            {/* 전체화면 토글 */}
            <button
              onClick={toggleFullscreen}
              className="p-1.5 hover:bg-white/20 rounded-full transition-colors"
            >
              {isFullscreen ? (
                <Minimize className="w-5 h-5 text-white" />
              ) : (
                <Maximize className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 음소거 표시 (우상단) */}
      {isMuted && !showControls && (
        <div className="absolute top-3 right-3">
          <button
            onClick={toggleMute}
            className="p-2 bg-black/60 hover:bg-black/80 rounded-full transition-colors"
          >
            <VolumeX className="w-4 h-4 text-white" />
          </button>
        </div>
      )}

      {/* GIF 표시 (GIF 타입인 경우에만) */}
      {isGif && (
        <div className="absolute bottom-3 left-3 px-1.5 py-0.5 bg-black/60 rounded text-xs font-bold text-white">
          GIF
        </div>
      )}
    </div>
  )
}
