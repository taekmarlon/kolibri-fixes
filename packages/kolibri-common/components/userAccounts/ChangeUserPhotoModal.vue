<template>

  <KModal
    :title="changePhotoHeader$()"
    :submitText="coreStrings.saveAction$()"
    :cancelText="coreStrings.cancelAction$()"
    :submitDisabled="!hasChanges || saving"
    @submit="savePhoto"
    @cancel="$emit('close')"
  >
    <div class="photo-modal-content">
      <div class="user-header">
        <UserAvatar
          :picture="previewUrl || user.picture"
          :name="user.full_name || user.username"
          :size="88"
        />
        <div class="user-meta">
          <h2 class="user-full-name">
            {{ user.full_name }}
          </h2>
          <p
            class="user-username"
            :style="{ color: $themeTokens.annotation }"
          >
            {{ user.username }}
          </p>
          <UserTypeDisplay
            v-if="user.kind"
            :userType="user.kind"
            :omitLearner="false"
          />
        </div>
      </div>

      <div class="photo-actions">
        <input
          ref="fileInputRef"
          type="file"
          accept="image/png, image/jpeg, image/jpg, image/webp, image/gif"
          class="hidden-file-input"
          @change="handleFileChange"
        >

        <KButton
          :text="choosePhotoAction$()"
          appearance="basic-link"
          :disabled="saving"
          @click="triggerFilePicker"
        />

        <KButton
          v-if="user.picture || selectedFile"
          :text="removePhotoAction$()"
          appearance="basic-link"
          :appearanceOverrides="{ color: $themeTokens.error }"
          :disabled="saving"
          @click="handleRemoveAction"
        />
      </div>

      <p
        class="file-notice"
        :style="{ color: $themeTokens.annotation }"
      >
        {{ fileSizeNotice$() }}
      </p>

      <KCircularLoader
        v-if="saving"
        :size="24"
        class="loader"
      />

      <div
        v-if="errorMessage"
        class="error-message"
        :style="{ color: $themeTokens.error }"
      >
        {{ errorMessage }}
      </div>
    </div>
  </KModal>

</template>


<script>

  import { ref, computed } from 'vue';
  import client from 'kolibri/client';
  import { coreStrings } from 'kolibri/uiText/commonCoreStrings';
  import { createTranslator } from 'kolibri/utils/i18n';
  import useSnackbar from 'kolibri/composables/useSnackbar';
  import UserTypeDisplay from 'kolibri-common/components/UserTypeDisplay';
  import UserAvatar from 'kolibri-common/components/userAccounts/UserAvatar';

  const photoModalStrings = createTranslator('ChangeUserPhotoModalStrings', {
    changePhotoHeader: {
      message: 'Change profile picture',
      context: 'Title of the modal for changing a user profile photo',
    },
    choosePhotoAction: {
      message: 'Choose picture',
      context: 'Button label to pick a picture from file system',
    },
    removePhotoAction: {
      message: 'Remove picture',
      context: 'Button label to remove the current user profile picture',
    },
    fileSizeNotice: {
      message: 'Supported formats: PNG, JPG, GIF, WEBP. Maximum size: 5 MB.',
      context: 'Notice about supported image types and max size limit',
    },
    fileSizeExceededError: {
      message: 'Image file size exceeds the 5MB maximum limit. Please choose a smaller image.',
      context: 'Error message when an uploaded image exceeds 5MB',
    },
    unsupportedFileTypeError: {
      message: 'Unsupported image file type. Please select a PNG, JPG, GIF, or WEBP image.',
      context: 'Error message when file is not a supported image format',
    },
    photoUpdatedSuccess: {
      message: 'Profile picture updated successfully',
      context: 'Notification message when photo is updated',
    },
    photoRemovedSuccess: {
      message: 'Profile picture removed successfully',
      context: 'Notification message when photo is removed',
    },
  });

  const MAX_FILE_SIZE = 5 * 1024 * 1024;
  const ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webp'];

  export default {
    name: 'ChangeUserPhotoModal',
    components: {
      UserAvatar,
      UserTypeDisplay,
    },
    props: {
      user: {
        type: Object,
        required: true,
      },
    },
    setup(props, { emit }) {
      const fileInputRef = ref(null);
      const selectedFile = ref(null);
      const previewUrl = ref(null);
      const isRemoving = ref(false);
      const saving = ref(false);
      const errorMessage = ref('');

      const { createSnackbar } = useSnackbar();

      const {
        changePhotoHeader$,
        choosePhotoAction$,
        removePhotoAction$,
        fileSizeNotice$,
        fileSizeExceededError$,
        unsupportedFileTypeError$,
        photoUpdatedSuccess$,
        photoRemovedSuccess$,
      } = photoModalStrings;

      const hasChanges = computed(() => {
        return Boolean(selectedFile.value) || isRemoving.value;
      });

      function triggerFilePicker() {
        if (fileInputRef.value) {
          fileInputRef.value.click();
        }
      }

      function handleFileChange(event) {
        errorMessage.value = '';
        const files = event.target?.files;
        if (!files || files.length === 0) {
          return;
        }

        const file = files[0];
        const lowerName = file.name.toLowerCase();
        const isAllowed = ALLOWED_EXTENSIONS.some(ext => lowerName.endsWith(ext));

        if (!isAllowed) {
          errorMessage.value = unsupportedFileTypeError$();
          return;
        }

        if (file.size > MAX_FILE_SIZE) {
          errorMessage.value = fileSizeExceededError$();
          return;
        }

        selectedFile.value = file;
        isRemoving.value = false;

        const reader = new FileReader();
        reader.onload = e => {
          previewUrl.value = e.target.result;
        };
        reader.readAsDataURL(file);
      }

      function handleRemoveAction() {
        errorMessage.value = '';
        selectedFile.value = null;
        previewUrl.value = null;
        isRemoving.value = true;
        if (fileInputRef.value) {
          fileInputRef.value.value = '';
        }
      }

      async function savePhoto() {
        errorMessage.value = '';
        saving.value = true;

        try {
          if (isRemoving.value) {
            const url = `/api/auth/facilityuser/${props.user.id}/delete_picture/`;
            await client({
              url,
              method: 'POST',
            });
            createSnackbar(photoRemovedSuccess$());
            emit('updated', { userId: props.user.id, picture: null });
            emit('close');
          } else if (selectedFile.value) {
            const formData = new FormData();
            formData.append('file', selectedFile.value);
            const url = `/api/auth/facilityuser/${props.user.id}/upload_picture/`;
            const response = await client({
              url,
              method: 'POST',
              data: formData,
            });
            createSnackbar(photoUpdatedSuccess$());
            emit('updated', { userId: props.user.id, picture: response.data.picture });
            emit('close');
          }
        } catch (err) {
          saving.value = false;
          const detail = err?.response?.data?.detail;
          errorMessage.value = detail || err.message || 'An error occurred while saving the picture.';
        }
      }

      return {
        fileInputRef,
        selectedFile,
        previewUrl,
        isRemoving,
        saving,
        errorMessage,
        hasChanges,
        triggerFilePicker,
        handleFileChange,
        handleRemoveAction,
        savePhoto,
        coreStrings,
        changePhotoHeader$,
        choosePhotoAction$,
        removePhotoAction$,
        fileSizeNotice$,
      };
    },
  };

</script>


<style lang="scss" scoped>

  .photo-modal-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 0;
    text-align: center;
  }

  .user-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
  }

  .user-meta {
    margin-top: 12px;
  }

  .user-full-name {
    margin: 0 0 4px;
    font-size: 1.2rem;
  }

  .user-username {
    margin: 0 0 8px;
    font-size: 0.9rem;
  }

  .hidden-file-input {
    display: none;
  }

  .photo-actions {
    display: flex;
    gap: 16px;
    align-items: center;
    justify-content: center;
    margin-bottom: 12px;
  }

  .file-notice {
    margin: 4px 0 12px;
    font-size: 0.8rem;
  }

  .loader {
    margin: 8px 0;
  }

  .error-message {
    margin-top: 8px;
    font-size: 0.9rem;
    font-weight: bold;
  }

</style>
