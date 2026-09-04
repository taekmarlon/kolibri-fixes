import { render, screen, fireEvent } from '@testing-library/vue';
import YouTubePlayer from '../YouTubePlayer.vue';

describe('YouTubePlayer', () => {
  it('renders correctly with a standard youtube.com watch URL', () => {
    render(YouTubePlayer, {
      props: {
        title: 'Cell Division Video',
        videoUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
      },
    });

    expect(screen.getByText('Cell Division Video')).toBeTruthy();
    const iframe = document.querySelector('iframe');
    expect(iframe).toBeTruthy();
    expect(iframe.getAttribute('src')).toBe(
      'https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0&modestbranding=1&enablejsapi=1'
    );
  });

  it('renders correctly with a youtu.be short URL', () => {
    render(YouTubePlayer, {
      props: {
        videoUrl: 'https://youtu.be/abcdefghijk',
      },
    });

    const iframe = document.querySelector('iframe');
    expect(iframe).toBeTruthy();
    expect(iframe.getAttribute('src')).toContain('abcdefghijk');
  });

  it('toggles fullscreen state on button click', async () => {
    const { container } = render(YouTubePlayer, {
      props: {
        videoId: 'dQw4w9WgXcQ',
      },
    });

    const fullscreenBtn = screen.getByRole('button', { name: /fullscreen/i });
    expect(container.firstChild.classList.contains('is-fullscreen')).toBe(false);

    await fireEvent.click(fullscreenBtn);
    expect(container.firstChild.classList.contains('is-fullscreen')).toBe(true);

    await fireEvent.click(fullscreenBtn);
    expect(container.firstChild.classList.contains('is-fullscreen')).toBe(false);
  });

  it('displays an invalid URL message when given empty or invalid input', () => {
    render(YouTubePlayer, {
      props: {
        videoUrl: 'not_a_valid_youtube_link',
      },
    });

    expect(
      screen.getByText(/Please provide a valid YouTube video URL or ID/i)
    ).toBeTruthy();
  });
});
