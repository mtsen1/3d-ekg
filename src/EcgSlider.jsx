import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export default function EcgSlider({ data, currentStep, onStepChange }) {
  const svgRef = useRef(null);

  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    // 1. DIMENSIONS & MARGIN CONFIGURATION
    const containerWidth = svgRef.current.parentElement.clientWidth;
    const containerHeight = svgRef.current.parentElement.clientHeight;

    const margin = { top: 24, right: 24, bottom: 24, left: 24 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Define the core SVG container group
    const g = svg
      .attr('width', containerWidth)
      .attr('height', containerHeight)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // 2. SCALES SETUP WITH BUFFERS
    const xScale = d3.scaleLinear()
      .domain([0, data.length - 1])
      .range([0, width]);

    const minRaw = d3.min(data, d => d.raw);
    const maxRaw = d3.max(data, d => d.raw);
    const rawRange = maxRaw - minRaw || 1.0;

    const bufferedMin = minRaw - (rawRange * 0.15);
    const bufferedMax = maxRaw + (rawRange * 0.15);

    const yScale = d3.scaleLinear()
      .domain([bufferedMin, bufferedMax])
      .range([height, 0]);

    // 3. DEFINE THE DYNAMIC COLOR PALETTE
    const palette = {
      qrs: '#4361ee',       // Royal Blue
      tWave: '#b7094c',     // Deep Burgundy/Red
      pWave: '#f77f00',     // Bright Orange
      baseline: '#a7c957'   // Lime/Resting Green
    };

    const getHexColor = (phaseString) => {
      const phase = phaseString || "";
      if (phase.includes('QRS')) return palette.qrs;
      if (phase.includes('T Wave') || phase.includes('T wave')) return palette.tWave;
      if (phase.includes('P Wave') || phase.includes('P wave')) return palette.pWave;
      return palette.baseline;
    };

    // 4. INJECT THE LIVE LINEAR GRADIENT STOPS
    // We create a unique gradient definition in the SVG defs layer
    const defs = svg.append('defs');
    const trailGradient = defs.append('linearGradient')
      .attr('id', 'ecg-trail-gradient')
      .attr('x1', '0%')
      .attr('y1', '0%')
      .attr('x2', '100%')
      .attr('y2', '0%'); // Horizontal gradient mapping

    // Calculate the exact percentage position of the current scrubber handle
    const currentPct = (currentStep / (data.length - 1)) * 100;

    // Loop through the dataset to construct the gradient stops up to the currentStep
    data.forEach((d, i) => {
      const pointPct = (i / (data.length - 1)) * 100;
      
      // Only paint color stops for historical data behind the scrubber line
      if (i <= currentStep) {
        trailGradient.append('stop')
          .attr('offset', `${pointPct}%`)
          .attr('stop-color', getHexColor(d.phase || d.Phase))
          .attr('stop-opacity', 0.25); // Soft backdrop glow opacity
      }
    });

    // Add a final transparent drop-off stop right at the scrubber handle index
    // so any upcoming unvisited data points remain clean and uncolored
    trailGradient.append('stop')
      .attr('offset', `${currentPct}%`)
      .attr('stop-color', '#ffffff')
      .attr('stop-opacity', 0);

    // 5. GENERATE AND DRAW THE GLOWING AREA UNDER THE TRACE
    // The area bounds the space stretching from the baseline floor up to the signal path
    const areaGenerator = d3.area()
      .x((d, i) => xScale(i))
      .y0(height) // Baseline anchor floor
      .y1(d => yScale(d.raw))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(data)
      .attr('fill', 'url(#ecg-trail-gradient)') // Bind to our dynamic gradient layer!
      .attr('d', areaGenerator);

    // 6. DRAW THE BACKGROUND ECG TRACE LINE
    const lineGenerator = d3.line()
      .x((d, i) => xScale(i))
      .y(d => yScale(d.raw))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#1e293b') // Deep Slate trace line
      .attr('stroke-width', 2)
      .attr('d', lineGenerator);

    // 7. DRAW THE ACTIVE TIMELINE VERTICAL SCRUBBER LINE
    g.append('line')
      .attr('x1', xScale(currentStep))
      .attr('y1', 0)
      .attr('x2', xScale(currentStep))
      .attr('y2', height)
      .attr('stroke', '#ef4444') 
      .attr('stroke-width', 2);

    // 8. DRAW THE GLIDING TARGET ORB ON THE 2D TRACE
    g.append('circle')
      .attr('cx', xScale(currentStep))
      .attr('cy', yScale(data[currentStep] ? data[currentStep].raw : 0))
      .attr('r', 5)
      .attr('fill', '#ef4444');

    // 9. GESTURE CAPTURE RECTANGLE INTERCEPTOR
    const handleScrubUpdate = (event) => {
      const [mouseX] = d3.pointer(event, g.node());
      const clampedX = Math.max(0, Math.min(width, mouseX));
      const calculatedIndex = Math.round(xScale.invert(clampedX));
      
      if (calculatedIndex >= 0 && calculatedIndex < data.length) {
        onStepChange(calculatedIndex);
      }
    };

    g.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'transparent')
      .style('cursor', 'ew-resize') 
      .call(
        d3.drag()
          .on('start', handleScrubUpdate)
          .on('drag', handleScrubUpdate)
      );

  }, [data, currentStep, onStepChange]);

  return <svg ref={svgRef} className="w-full h-full block overflow-visible" />;
}