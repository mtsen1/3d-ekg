import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function Ecg3DSpace({ data, currentStep }) {
  const mountRef = useRef(null);
  
  const lineRef = useRef(null);
  const trackerRef = useRef(null);
  const centerRef = useRef(new THREE.Vector3());

  // HOOK 1: INITIALIZE CANVAS & GRAPHICS ENVIRONMENT
  useEffect(() => {
    if (!mountRef.current || !data || data.length === 0) return;

    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;
    mountRef.current.innerHTML = ''; 

    const scene = new THREE.Scene();
    scene.background = new THREE.Color('#f8fafc'); 

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
    scene.add(ambientLight);

    // REGIONAL HEALTH ATTRIBUTE PALETTE
    const cQrsBlue = new THREE.Color('#4361ee');       
    const cTWaveRed = new THREE.Color('#b7094c');      
    const cPWaveOrange = new THREE.Color('#f77f00');   
    const cBaselineGreen = new THREE.Color('#a7c957'); 

    const getTargetColor = (phaseString) => {
      const phase = phaseString || "";
      if (phase.includes('QRS')) return cQrsBlue;
      if (phase.includes('T Wave') || phase.includes('T wave')) return cTWaveRed;
      if (phase.includes('P Wave') || phase.includes('P wave')) return cPWaveOrange;
      return cBaselineGreen;
    };

    // GENERATE ATTRACTOR PATH MATRIX
    const points = data.map(d => new THREE.Vector3(d.x * 12, d.y * 12, d.z * 12));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);

    geometry.computeBoundingBox();
    geometry.boundingBox.getCenter(centerRef.current);
    geometry.center(); // Lock anchor to the true midpoint object center

    const colors = [];
    data.forEach((d) => {
      const vertexColor = getTargetColor(d.phase || d.Phase);
      colors.push(vertexColor.r, vertexColor.g, vertexColor.b);
    });
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.LineBasicMaterial({
      vertexColors: true,
      linewidth: 3,
      transparent: true,
      opacity: 0.9
    });

    const attractorLine = new THREE.Line(geometry, material);
    scene.add(attractorLine);
    lineRef.current = attractorLine; 

    camera.position.set(0, 15, 25);
    camera.lookAt(0, 0, 0);

   // 4. INITIALIZE TRACKER ORB NODE (Reduced radius from 0.5 to 0.2)
    const sphereGeometry = new THREE.SphereGeometry(0.2, 32, 32);
    const sphereMaterial = new THREE.MeshBasicMaterial({ color: 0xef4444 }); 
    const trackerNode = new THREE.Mesh(sphereGeometry, sphereMaterial);
    
    // CRITICAL FIX: Add the tracker node directly as a child mesh of the line!
    // This forces the orb to automatically inherit the line's ambient rotation matrices natively.
    attractorLine.add(trackerNode);
    trackerRef.current = trackerNode; 

    // HARDWARE-ACCELERATED REFRESH LOOP
    let animationFrameId;
    let rotationAngle = 0;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Apply uniform ambient spin velocity
      rotationAngle += 0.004;
      if (lineRef.current) lineRef.current.rotation.y = rotationAngle;

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      geometry.dispose();
      material.dispose();
      sphereGeometry.dispose();
      sphereMaterial.dispose();
    };
  }, [data]);

  // HOOK 2: LIVE EDGE-LOCK CONTROLLER (Fires instantly when user drags cursor)
  useEffect(() => {
    if (!lineRef.current || !trackerRef.current || !data || data.length === 0) return;

    // A. Constrain the active slice range rendering
    lineRef.current.geometry.setDrawRange(0, currentStep + 1);

    // B. Pin the orb directly to the local space of the leading data vertex coordinate
    const activePoint = data[currentStep];
    if (activePoint) {
      trackerRef.current.position.set(
        (activePoint.x * 12) - centerRef.current.x,
        (activePoint.y * 12) - centerRef.current.y,
        (activePoint.z * 12) - centerRef.current.z
      );
    }
  }, [currentStep, data]);

  return <div ref={mountRef} className="w-full h-full min-h-[400px] rounded-2xl overflow-hidden" />;
}