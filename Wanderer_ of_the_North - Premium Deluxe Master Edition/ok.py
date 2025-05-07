if self.boss_intro_playing and not self.boss_intro_video_done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == BOSS_MUSIC_EVENT:
            print("Tocando música do boss após 19s do vídeo.")
            self.play_music("boss_music")
            self.boss_music_playing = True

    self.calculate_camera_offset()
    return
