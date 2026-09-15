import { render, screen, fireEvent } from '@testing-library/vue';
import '@testing-library/jest-dom';
import UserAvatar from '../UserAvatar.vue';

describe('UserAvatar', () => {
  it('renders fallback icon when no picture is provided', () => {
    const { container } = render(UserAvatar, {
      props: {
        name: 'Jane Doe',
      },
    });
    expect(container.querySelector('img')).toBeNull();
    expect(container.querySelector('.user-avatar-fallback')).toBeInTheDocument();
  });

  it('renders img tag when picture prop is provided', () => {
    render(UserAvatar, {
      props: {
        picture: '/media/user_photos/avatar.png',
        name: 'Jane Doe',
      },
    });
    const img = screen.getByRole('img');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', '/media/user_photos/avatar.png');
    expect(img).toHaveAttribute('alt', 'Jane Doe');
  });

  it('renders img tag when user object with picture is provided', () => {
    render(UserAvatar, {
      props: {
        user: {
          username: 'janedoe',
          full_name: 'Jane Doe',
          picture: '/media/user_photos/janedoe.jpg',
        },
      },
    });
    const img = screen.getByRole('img');
    expect(img).toBeInTheDocument();
    expect(img).toHaveAttribute('src', '/media/user_photos/janedoe.jpg');
    expect(img).toHaveAttribute('alt', 'Jane Doe');
  });

  it('falls back to icon when image encounters load error', async () => {
    const { container } = render(UserAvatar, {
      props: {
        picture: '/media/user_photos/broken.png',
        name: 'Broken Image User',
      },
    });
    const img = screen.getByRole('img');
    expect(img).toBeInTheDocument();

    await fireEvent.error(img);

    expect(container.querySelector('img')).toBeNull();
    expect(container.querySelector('.user-avatar-fallback')).toBeInTheDocument();
  });
});
