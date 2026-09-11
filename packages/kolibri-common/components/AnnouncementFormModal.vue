<template>
  <KModal
    :title="isEditing ? editModalTitle$() : createModalTitle$()"
    :submitText="saveBtn$()"
    :cancelText="cancelBtn$()"
    size="medium"
    :submitDisabled="!form.title || !form.body || saving"
    @submit="onSubmit"
    @cancel="$emit('close')"
  >
    <!-- Title -->
    <KTextbox
      v-model="form.title"
      :label="titleLabel$()"
      :maxlength="200"
      :autofocus="true"
      class="form-field"
    />

    <!-- Type selector -->
    <KSelect
      v-model="typeOption"
      :label="typeLabel$()"
      :options="typeOptions"
      class="form-field"
    />

    <!-- Scope selector -->
    <KSelect
      v-model="scopeOption"
      :label="scopeLabel$()"
      :options="scopeOptions"
      class="form-field"
    />

    <!-- Body -->
    <KTextbox
      v-model="form.body"
      :label="bodyLabel$()"
      :textinputtype="'textarea'"
      :maxlength="2000"
      :rows="4"
      class="form-field"
    />

    <!-- Event date (shown only when type = event) -->
    <KTextbox
      v-if="form.announcement_type === 'event'"
      v-model="form.event_date"
      :label="eventDateLabel$()"
      type="datetime-local"
      class="form-field"
    />

    <!-- Expiry date -->
    <KTextbox
      v-model="form.expiry_date"
      :label="expiryDateLabel$()"
      type="datetime-local"
      class="form-field"
    />

    <!-- Link URL -->
    <KTextbox
      v-model="form.link_url"
      :label="linkUrlLabel$()"
      :placeholder="linkUrlPlaceholder$()"
      class="form-field"
    />

    <!-- Pin checkbox -->
    <div class="pin-row">
      <KCheckbox
        :label="pinLabel$()"
        :checked="form.is_pinned"
        @change="form.is_pinned = $event"
      />
    </div>

    <!-- Error notice -->
    <p v-if="error" class="error-msg" :style="{ color: $themePalette.red.v_700 }">
      {{ error }}
    </p>
  </KModal>
</template>

<script>
  import { ref, computed, onMounted } from 'vue';
  import { createTranslator } from 'kolibri/utils/i18n';
  import AnnouncementResource from 'kolibri-common/apiResources/AnnouncementResource';

  const strings = createTranslator('AnnouncementFormModalStrings', {
    createModalTitle: { message: 'New School Announcement', context: 'Modal title for creating announcement' },
    editModalTitle: { message: 'Edit Announcement', context: 'Modal title for editing announcement' },
    titleLabel: { message: 'Title', context: 'Announcement title field label' },
    bodyLabel: { message: 'Content / Details', context: 'Announcement body field label' },
    typeLabel: { message: 'Announcement Type', context: 'Announcement type selector label' },
    scopeLabel: { message: 'Target Audience / Scope', context: 'Announcement scope selector label' },
    eventDateLabel: { message: 'Event Date & Time', context: 'Event date field label' },
    expiryDateLabel: { message: 'Expiration Date (optional)', context: 'Expiry date field label' },
    linkUrlLabel: { message: 'External Link / DepEd URL (optional)', context: 'Link URL field label' },
    linkUrlPlaceholder: { message: 'https://deped.gov.ph/...', context: 'URL field placeholder' },
    pinLabel: { message: 'Pin this announcement (always show at top)', context: 'Pin checkbox label' },
    saveBtn: { message: 'Save Announcement', context: 'Save button' },
    cancelBtn: { message: 'Cancel', context: 'Cancel button' },
    typeGeneral: { message: 'General Notice', context: 'Announcement type option' },
    typeEvent: { message: 'School Event', context: 'Announcement type option' },
    typeDeped: { message: 'DepEd Memorandum', context: 'Announcement type option' },
    typeUrgent: { message: 'Urgent Bulletin', context: 'Announcement type option' },
    scopeClass: { message: 'Class Only', context: 'Scope option: class-level' },
    scopeFacility: { message: 'Entire School (Facility-Wide)', context: 'Scope option: facility-wide' },
  });

  export default {
    name: 'AnnouncementFormModal',
    props: {
      announcement: {
        type: Object,
        default: null,
      },
      classId: {
        type: String,
        default: null,
      },
      facilityId: {
        type: String,
        default: null,
      },
    },
    emits: ['close', 'saved'],
    setup(props, { emit }) {
      const saving = ref(false);
      const error = ref('');

      const {
        createModalTitle$,
        editModalTitle$,
        titleLabel$,
        bodyLabel$,
        typeLabel$,
        scopeLabel$,
        eventDateLabel$,
        expiryDateLabel$,
        linkUrlLabel$,
        linkUrlPlaceholder$,
        pinLabel$,
        saveBtn$,
        cancelBtn$,
        typeGeneral$,
        typeEvent$,
        typeDeped$,
        typeUrgent$,
        scopeClass$,
        scopeFacility$,
      } = strings;

      const isEditing = computed(() => !!props.announcement);

      const typeOptions = [
        { value: 'general', label: '📢 General Notice' },
        { value: 'event', label: '📅 School Event' },
        { value: 'deped_memo', label: '📋 DepEd Memorandum' },
        { value: 'urgent', label: '🚨 Urgent Bulletin' },
      ];

      const scopeOptions = [
        { value: 'facility', label: '🏛️ Entire School (Facility-Wide)' },
        { value: 'class', label: '🏫 Class Only' },
      ];

      const form = ref({
        title: '',
        body: '',
        announcement_type: 'general',
        scope: props.facilityId && !props.classId ? 'facility' : (props.classId ? 'class' : 'facility'),
        collection: props.facilityId || props.classId || '',
        event_date: '',
        expiry_date: '',
        link_url: '',
        is_pinned: false,
      });

      // Sync selectors with form
      const typeOption = computed({
        get: () => typeOptions.find(o => o.value === form.value.announcement_type) || typeOptions[0],
        set: val => { form.value.announcement_type = val.value; },
      });

      const scopeOption = computed({
        get: () => scopeOptions.find(o => o.value === form.value.scope) || scopeOptions[0],
        set: val => {
          form.value.scope = val.value;
          if (val.value === 'facility' && props.facilityId) {
            form.value.collection = props.facilityId;
          } else if (val.value === 'class' && props.classId) {
            form.value.collection = props.classId;
          }
        },
      });

      onMounted(() => {
        if (props.announcement) {
          const a = props.announcement;
          form.value = {
            title: a.title || '',
            body: a.body || '',
            announcement_type: a.announcement_type || 'general',
            scope: a.scope || (props.facilityId ? 'facility' : 'class'),
            collection: a.collection || props.facilityId || props.classId,
            event_date: a.event_date ? a.event_date.slice(0, 16) : '',
            expiry_date: a.expiry_date ? a.expiry_date.slice(0, 16) : '',
            link_url: a.link_url || '',
            is_pinned: a.is_pinned || false,
          };
        }
      });

      async function onSubmit() {
        saving.value = true;
        error.value = '';

        const payload = {
          title: form.value.title,
          body: form.value.body,
          announcement_type: form.value.announcement_type,
          scope: form.value.scope,
          collection: form.value.collection || props.facilityId || props.classId,
          is_pinned: form.value.is_pinned,
          link_url: form.value.link_url,
        };

        if (form.value.event_date) {
          payload.event_date = new Date(form.value.event_date).toISOString();
        }
        if (form.value.expiry_date) {
          payload.expiry_date = new Date(form.value.expiry_date).toISOString();
        }

        try {
          let result;
          if (isEditing.value) {
            result = await AnnouncementResource.saveModel({
              id: props.announcement.id,
              data: payload,
            });
          } else {
            result = await AnnouncementResource.saveModel({
              data: payload,
            });
          }
          emit('saved', result);
        } catch (e) {
          error.value = e?.message || 'Failed to save announcement. Please try again.';
        } finally {
          saving.value = false;
        }
      }

      return {
        form,
        typeOptions,
        typeOption,
        scopeOptions,
        scopeOption,
        isEditing,
        saving,
        error,
        onSubmit,
        createModalTitle$,
        editModalTitle$,
        titleLabel$,
        bodyLabel$,
        typeLabel$,
        scopeLabel$,
        eventDateLabel$,
        expiryDateLabel$,
        linkUrlLabel$,
        linkUrlPlaceholder$,
        pinLabel$,
        saveBtn$,
        cancelBtn$,
        typeGeneral$,
        typeEvent$,
        typeDeped$,
        typeUrgent$,
        scopeClass$,
        scopeFacility$,
      };
    },
  };
</script>

<style lang="scss" scoped>

  .form-field {
    margin-bottom: 16px;
  }

  .pin-row {
    margin: 8px 0 16px;
  }

  .error-msg {
    font-size: 0.85rem;
    margin: 8px 0 0;
  }

</style>
