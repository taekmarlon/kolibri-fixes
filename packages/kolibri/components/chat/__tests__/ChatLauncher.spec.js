/* eslint-disable kolibri/tests-no-hardcoded-strings */
import { render, screen, fireEvent } from '@testing-library/vue';
import ChatLauncher, { launcherStrings } from '../ChatLauncher';

describe('ChatLauncher', () => {
  it('renders the floating launcher button with PHIEDU aria-label and title', () => {
    render(ChatLauncher, {
      props: {
        isOpen: false,
        unreadCount: 0,
      },
    });

    const btn = screen.getByRole('button', { name: launcherStrings.$tr('phieduMessages') });
    expect(btn).toBeInTheDocument();
    expect(btn).toHaveAttribute('title', launcherStrings.$tr('openMessages'));
  });

  it('displays the unread badge counter when unreadCount > 0', () => {
    render(ChatLauncher, {
      props: {
        isOpen: false,
        unreadCount: 5,
      },
    });

    expect(screen.getByText(/5/)).toBeInTheDocument();
  });

  it('caps unread badge counter at 99+ when greater than 99', () => {
    render(ChatLauncher, {
      props: {
        isOpen: false,
        unreadCount: 150,
      },
    });

    expect(screen.getByText(/99\+/)).toBeInTheDocument();
  });

  it('emits toggle event when clicked', async () => {
    const { emitted } = render(ChatLauncher, {
      props: {
        isOpen: false,
        unreadCount: 0,
      },
    });

    const btn = screen.getByRole('button', { name: launcherStrings.$tr('phieduMessages') });
    await fireEvent.click(btn);

    expect(emitted().toggle).toBeTruthy();
    expect(emitted().toggle.length).toBe(1);
  });

  it('shows close title when isOpen is true', () => {
    render(ChatLauncher, {
      props: {
        isOpen: true,
        unreadCount: 3,
      },
    });

    const btn = screen.getByRole('button', { name: launcherStrings.$tr('phieduMessages') });
    expect(btn).toHaveAttribute('title', launcherStrings.$tr('closeMessages'));
  });
});
