import { useState, useRef, useEffect } from 'react';

interface Position {
  x: number;
  y: number;
}

interface DragState {
  isDragging: boolean;
  position: Position;
  dragStart: Position;
  initialPosition: Position;
}

export function useDrag() {
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    position: { x: 0, y: 0 },
    dragStart: { x: 0, y: 0 },
    initialPosition: { x: 0, y: 0 }
  });

  const dragRef = useRef<HTMLDivElement>(null);
  const handleRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!dragRef.current || !handleRef.current) return;
    
    // Only start dragging if clicking on the drag handle
    const handleElement = handleRef.current;
    if (!handleElement.contains(e.target as Node)) return;

    const rect = dragRef.current.getBoundingClientRect();
    const startX = e.clientX - rect.left;
    const startY = e.clientY - rect.top;

    setDragState(prev => ({
      ...prev,
      isDragging: true,
      dragStart: { x: startX, y: startY },
      initialPosition: { x: rect.left, y: rect.top }
    }));

    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragState.isDragging || !dragRef.current) return;

      const newX = e.clientX - dragState.dragStart.x;
      const newY = e.clientY - dragState.dragStart.y;

      // Constrain to viewport bounds
      const maxX = window.innerWidth - dragRef.current.offsetWidth;
      const maxY = window.innerHeight - dragRef.current.offsetHeight;

      const constrainedX = Math.max(0, Math.min(newX, maxX));
      const constrainedY = Math.max(0, Math.min(newY, maxY));

      setDragState(prev => ({
        ...prev,
        position: { x: constrainedX, y: constrainedY }
      }));
    };

    const handleMouseUp = () => {
      setDragState(prev => ({
        ...prev,
        isDragging: false
      }));
    };

    if (dragState.isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'grabbing';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [dragState.isDragging, dragState.dragStart]);

  return {
    dragRef,
    handleRef,
    isDragging: dragState.isDragging,
    position: dragState.position,
    handleMouseDown,
    dragProps: {
      style: {
        position: 'fixed' as const,
        left: dragState.position.x,
        top: dragState.position.y,
        cursor: dragState.isDragging ? 'grabbing' : 'auto',
      },
      onMouseDown: handleMouseDown,
    },
    handleProps: {
      style: {
        cursor: 'grab',
      }
    }
  };
}