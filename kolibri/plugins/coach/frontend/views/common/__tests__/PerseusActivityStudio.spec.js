import { render, screen, fireEvent } from '@testing-library/vue';
import '@testing-library/jest-dom';
import PerseusActivityStudio from '../PerseusActivityStudio.vue';

describe('PerseusActivityStudio', () => {
  it('renders the studio with title input, subject category, and template cards', () => {
    render(PerseusActivityStudio);

    expect(screen.getByText('Activity Title')).toBeInTheDocument();
    expect(screen.getByText('Multi-Subject Template Library')).toBeInTheDocument();
    expect(screen.getByText('Reading Comprehension & Analysis')).toBeInTheDocument();
    expect(screen.getByText('Grammar & Context Cloze')).toBeInTheDocument();
    expect(screen.getByText('Historical Event Timeline')).toBeInTheDocument();
    expect(screen.getByText('Government Powers & Branches')).toBeInTheDocument();
  });

  it('emits change event with valid Perseus item data when template is selected', async () => {
    const { emitted } = render(PerseusActivityStudio);

    const templateBtn = screen.getByText('Historical Event Timeline');
    await fireEvent.click(templateBtn);

    expect(emitted().change).toBeTruthy();
    const lastEmit = emitted().change[emitted().change.length - 1][0];
    expect(lastEmit.title).toContain('Timeline');
    expect(lastEmit.subject).toBe('history');
    expect(lastEmit.item).toBeDefined();
    expect(lastEmit.item.question).toBeDefined();
    expect(lastEmit.item.question.content).toContain('orderer');
    expect(lastEmit.item.question.widgets).toBeDefined();
  });

  it('renders widget insert toolbar with multi-subject widgets', () => {
    render(PerseusActivityStudio);

    expect(screen.getByText(/Reading Passage/i)).toBeInTheDocument();
    expect(screen.getByText(/Cloze Dropdown/i)).toBeInTheDocument();
    expect(screen.getByText(/Sequence Orderer/i)).toBeInTheDocument();
    expect(screen.getByText(/Concept Categorizer/i)).toBeInTheDocument();
    expect(screen.getByText(/Matching Pairs/i)).toBeInTheDocument();
  });

  it('allows adding and removing progressive hints', async () => {
    const { emitted } = render(PerseusActivityStudio);

    const addHintBtn = screen.getByRole('button', { name: /\+ Add Step Hint/i });
    await fireEvent.click(addHintBtn);

    expect(emitted().change).toBeTruthy();
    const lastEmit = emitted().change[emitted().change.length - 1][0];
    expect(lastEmit.item.hints.length).toBeGreaterThan(0);
  });
});
