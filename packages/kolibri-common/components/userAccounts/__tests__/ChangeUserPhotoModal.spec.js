import { render, screen, fireEvent, waitFor } from '@testing-library/vue';
import '@testing-library/jest-dom';
import client from 'kolibri/client';
import useSnackbar from 'kolibri/composables/useSnackbar';
import ChangeUserPhotoModal from '../ChangeUserPhotoModal.vue';

jest.mock('kolibri/client');
jest.mock('kolibri/composables/useSnackbar');

const mockCreateSnackbar = jest.fn();
useSnackbar.mockImplementation(() => ({
  createSnackbar: mockCreateSnackbar,
}));

describe('ChangeUserPhotoModal', () => {
  const userWithoutPhoto = {
    id: 'user-1',
    full_name: 'Alice Johnson',
    username: 'alice',
    kind: 'learner',
    picture: null,
  };

  const userWithPhoto = {
    id: 'user-2',
    full_name: 'Bob Smith',
    username: 'bob',
    kind: 'admin',
    picture: '/media/user_photos/bob.png',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders user information correctly', () => {
    render(ChangeUserPhotoModal, {
      props: {
        user: userWithoutPhoto,
      },
    });

    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    expect(screen.getByText('alice')).toBeInTheDocument();
    expect(screen.getByText('Choose picture')).toBeInTheDocument();
    expect(screen.queryByText('Remove picture')).not.toBeInTheDocument();
  });

  it('shows Remove picture button when user has an existing picture', () => {
    render(ChangeUserPhotoModal, {
      props: {
        user: userWithPhoto,
      },
    });

    expect(screen.getByText('Bob Smith')).toBeInTheDocument();
    expect(screen.getByText('Remove picture')).toBeInTheDocument();
  });

  it('shows validation error when invalid file type is selected', async () => {
    const { container } = render(ChangeUserPhotoModal, {
      props: {
        user: userWithoutPhoto,
      },
    });

    const fileInput = container.querySelector('input[type="file"]');
    const invalidFile = new File(['content'], 'document.pdf', { type: 'application/pdf' });

    Object.defineProperty(fileInput, 'files', {
      value: [invalidFile],
    });
    await fireEvent.change(fileInput);

    expect(
      screen.getByText(/Unsupported image file type. Please select a PNG, JPG, GIF, or WEBP image./),
    ).toBeInTheDocument();
  });

  it('removes picture and emits updated when Remove picture is clicked and saved', async () => {
    client.mockResolvedValue({ data: { success: true } });

    const { emitted } = render(ChangeUserPhotoModal, {
      props: {
        user: userWithPhoto,
      },
    });

    const removeBtn = screen.getByText('Remove picture');
    await fireEvent.click(removeBtn);

    const saveBtn = screen.getByText('Save');
    await fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(client).toHaveBeenCalledWith({
        url: '/api/auth/facilityuser/user-2/delete_picture/',
        method: 'POST',
      });
      expect(mockCreateSnackbar).toHaveBeenCalled();
      expect(emitted()).toHaveProperty('updated');
      expect(emitted().updated[0]).toEqual([{ userId: 'user-2', picture: null }]);
      expect(emitted()).toHaveProperty('close');
    });
  });

  it('uploads picture and emits updated when a valid image is selected and saved', async () => {
    client.mockResolvedValue({
      data: {
        success: true,
        picture: '/media/user_photos/new_alice.png',
      },
    });

    const { container, emitted } = render(ChangeUserPhotoModal, {
      props: {
        user: userWithoutPhoto,
      },
    });

    const fileInput = container.querySelector('input[type="file"]');
    const validFile = new File(['fake-png-content'], 'alice.png', { type: 'image/png' });

    Object.defineProperty(fileInput, 'files', {
      value: [validFile],
    });
    await fireEvent.change(fileInput);

    const saveBtn = screen.getByText('Save');
    await fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(client).toHaveBeenCalledWith(
        expect.objectContaining({
          url: '/api/auth/facilityuser/user-1/upload_picture/',
          method: 'POST',
        }),
      );
      expect(mockCreateSnackbar).toHaveBeenCalled();
      expect(emitted()).toHaveProperty('updated');
      expect(emitted().updated[0]).toEqual([
        { userId: 'user-1', picture: '/media/user_photos/new_alice.png' },
      ]);
      expect(emitted()).toHaveProperty('close');
    });
  });
});
