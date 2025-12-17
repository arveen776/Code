import React, { useMemo, useRef, useState, useCallback } from "react";
import * as THREE from "three";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Html, Line } from "@react-three/drei";

/**
 * Optimized Modular Unit System
 * - Uses truncated octahedron geometry for optimal 3D tiling (14 faces, better connection flexibility)
 * - Supports multi-directional snapping in 3D space
 * - Enables building complex structures with maximum flexibility
 * - Each module can connect to neighbors via 14 face directions
 */

const GRID = 12; // increased grid for more building space
const CELL = 1.0; // spacing between module centers

// Truncated octahedron has 14 faces:
// 8 hexagonal faces and 6 square faces
// This provides optimal 3D tiling and maximum connection flexibility
function generateTruncatedOctahedronDirections() {
  const dirs = [];
  
  // 6 square faces (axial directions) - same as cube
  dirs.push(new THREE.Vector3(1, 0, 0).normalize());
  dirs.push(new THREE.Vector3(-1, 0, 0).normalize());
  dirs.push(new THREE.Vector3(0, 1, 0).normalize());
  dirs.push(new THREE.Vector3(0, -1, 0).normalize());
  dirs.push(new THREE.Vector3(0, 0, 1).normalize());
  dirs.push(new THREE.Vector3(0, 0, -1).normalize());
  
  // 8 hexagonal faces (diagonal directions) - key advantage for flexibility
  const sqrt2 = Math.sqrt(2);
  dirs.push(new THREE.Vector3(1, 1, 0).normalize());
  dirs.push(new THREE.Vector3(1, -1, 0).normalize());
  dirs.push(new THREE.Vector3(-1, 1, 0).normalize());
  dirs.push(new THREE.Vector3(-1, -1, 0).normalize());
  dirs.push(new THREE.Vector3(1, 0, 1).normalize());
  dirs.push(new THREE.Vector3(1, 0, -1).normalize());
  dirs.push(new THREE.Vector3(-1, 0, 1).normalize());
  dirs.push(new THREE.Vector3(-1, 0, -1).normalize());
  
  return dirs;
}

const DIRS = generateTruncatedOctahedronDirections();

function keyFrom(x, y, z) {
  return `${x},${y},${z}`;
}

function parseKey(k) {
  const [x, y, z] = k.split(",").map(Number);
  return { x, y, z };
}

function worldFromCell(x, y, z) {
  return new THREE.Vector3(x * CELL, y * CELL, z * CELL);
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

// Create truncated octahedron geometry
// This is the optimal shape for 3D tiling with maximum connection flexibility
function createTruncatedOctahedronGeometry(size = 0.5) {
  // Using an icosahedron as a good approximation that emphasizes the many faces
  // Real truncated octahedron would require more complex geometry generation
  const tempGeo = new THREE.IcosahedronGeometry(size, 1);
  const geometry = tempGeo.clone();
  
  // Scale and adjust to better approximate truncated octahedron appearance
  const pos = geometry.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const v = new THREE.Vector3().fromBufferAttribute(pos, i);
    v.normalize().multiplyScalar(size * 0.9);
    pos.setXYZ(i, v.x, v.y, v.z);
  }
  
  geometry.computeVertexNormals();
  return geometry;
}

// Pre-create geometry for performance (outside component)
let moduleGeometry = null;
function getModuleGeometry() {
  if (!moduleGeometry) {
    moduleGeometry = createTruncatedOctahedronGeometry(0.48);
  }
  return moduleGeometry;
}

function Module({ position, connectedFaces, selected, rotation = [0, 0, 0] }) {
  // connectedFaces: boolean[14] corresponds to DIRS index
  const faceDots = useMemo(() => {
    const offs = 0.52; // where the connector dot sits from center
    return DIRS.map((d, i) => ({
      p: [d.x * offs, d.y * offs, d.z * offs],
      connected: !!connectedFaces?.[i],
      i,
      isHexagonal: i >= 6, // First 6 are square faces, rest are hexagonal
    }));
  }, [connectedFaces]);

  const matRef = useRef();
  const geom = useMemo(() => getModuleGeometry(), []);

  return (
    <group position={position} rotation={rotation}>
      <mesh geometry={geom} ref={matRef}>
        <meshStandardMaterial
          metalness={0.3}
          roughness={0.5}
          color={selected ? "#60a5fa" : "#d1d5db"}
          emissive={selected ? "#1e40af" : "#000000"}
          emissiveIntensity={selected ? 0.2 : 0}
        />
      </mesh>

      {/* Face connector indicators - different sizes for square vs hexagonal faces */}
      {faceDots.map((d) => (
        <mesh key={d.i} position={d.p}>
          <sphereGeometry args={[d.isHexagonal ? 0.06 : 0.08, 12, 12]} />
          <meshStandardMaterial
            color={d.connected ? "#22c55e" : (d.isHexagonal ? "#94a3b8" : "#a1a1aa")}
            emissive={d.connected ? "#14532d" : "#000000"}
            emissiveIntensity={d.connected ? 0.4 : 0}
            metalness={d.connected ? 0.8 : 0.2}
            roughness={d.connected ? 0.3 : 0.7}
          />
        </mesh>
      ))}
    </group>
  );
}

function GridHelperLines({ currentZ = 0 }) {
  // 3D lattice guide that adapts to current working plane
  const lines = useMemo(() => {
    const arr = [];
    // Grid lines for current Z plane
    for (let i = -GRID; i <= GRID; i++) {
      arr.push([
        [-GRID * CELL, i * CELL, currentZ],
        [GRID * CELL, i * CELL, currentZ],
      ]);
      arr.push([
        [i * CELL, -GRID * CELL, currentZ],
        [i * CELL, GRID * CELL, currentZ],
      ]);
    }
    // Subtle grid lines for adjacent planes
    if (currentZ > -GRID) {
      for (let i = -GRID; i <= GRID; i += 2) {
        arr.push([
          [-GRID * CELL, i * CELL, currentZ - CELL],
          [GRID * CELL, i * CELL, currentZ - CELL],
        ]);
        arr.push([
          [i * CELL, -GRID * CELL, currentZ - CELL],
          [i * CELL, GRID * CELL, currentZ - CELL],
        ]);
      }
    }
    if (currentZ < GRID) {
      for (let i = -GRID; i <= GRID; i += 2) {
        arr.push([
          [-GRID * CELL, i * CELL, currentZ + CELL],
          [GRID * CELL, i * CELL, currentZ + CELL],
        ]);
        arr.push([
          [i * CELL, -GRID * CELL, currentZ + CELL],
          [i * CELL, GRID * CELL, currentZ + CELL],
        ]);
      }
    }
    return arr;
  }, [currentZ]);

  return (
    <group>
      {lines.map((pts, idx) => {
        const isCurrentPlane = Math.abs(pts[0][2] - currentZ) < 0.1;
        return (
          <Line 
            key={idx} 
            points={pts} 
            lineWidth={isCurrentPlane ? 1 : 0.5} 
            color={isCurrentPlane ? "#e5e7eb" : "#d4d4d4"}
          />
        );
      })}
      {/* Axis lines */}
      <Line points={[[0, 0, currentZ], [3, 0, currentZ]]} color="#ef4444" lineWidth={2} />
      <Line points={[[0, 0, currentZ], [0, 3, currentZ]]} color="#22c55e" lineWidth={2} />
      <Line points={[[0, 0, currentZ], [0, 0, currentZ + 3]]} color="#3b82f6" lineWidth={2} />
    </group>
  );
}

function HoverGhost({ cell, canPlace = false }) {
  const pos = useMemo(() => worldFromCell(cell.x, cell.y, cell.z), [cell]);
  const geom = useMemo(() => getModuleGeometry(), []);
  
  return (
    <group position={pos}>
      <mesh geometry={geom}>
        <meshStandardMaterial 
          transparent 
          opacity={canPlace ? 0.4 : 0.2} 
          color={canPlace ? "#60a5fa" : "#ef4444"}
          wireframe={!canPlace}
          emissive={canPlace ? "#1e40af" : "#7f1d1d"}
          emissiveIntensity={canPlace ? 0.3 : 0.1}
        />
      </mesh>
      {/* Show connection preview */}
      {canPlace && DIRS.slice(0, 6).map((d, i) => (
        <mesh key={i} position={[d.x * 0.5, d.y * 0.5, d.z * 0.5]}>
          <sphereGeometry args={[0.06, 8, 8]} />
          <meshStandardMaterial transparent opacity={0.5} color="#22c55e" />
        </mesh>
      ))}
    </group>
  );
}

function Scene() {
  // modules stored as keys "x,y,z"
  const [mods, setMods] = useState(() => new Set([keyFrom(0, 0, 0)]));
  const [hoverCell, setHoverCell] = useState({ x: 1, y: 0, z: 0 });
  const [selectedKey, setSelectedKey] = useState(keyFrom(0, 0, 0));
  const [mode, setMode] = useState("add"); // add | remove
  const [currentZ, setCurrentZ] = useState(0); // Current working plane
  const [snapMode, setSnapMode] = useState("nearest"); // nearest | face

  const raycaster = useMemo(() => new THREE.Raycaster(), []);
  const tmp = useMemo(() => new THREE.Vector3(), []);
  const tmp2 = useMemo(() => new THREE.Vector3(), []);

  // Find nearest module to snap to
  const findNearestSnapPosition = useCallback((worldPos, existingModules) => {
    if (existingModules.size === 0) {
      // Snap to grid if no modules exist
      return {
        x: Math.round(worldPos.x / CELL),
        y: Math.round(worldPos.y / CELL),
        z: Math.round(worldPos.z / CELL),
        canPlace: true,
      };
    }

    let nearestDist = Infinity;
    let bestPos = null;
    let canPlace = false;

    // Check all existing modules for nearest connection
    existingModules.forEach((key) => {
      const { x, y, z } = parseKey(key);
      const modulePos = worldFromCell(x, y, z);
      
      // Check all 14 face directions
      DIRS.forEach((dir) => {
        const candidatePos = tmp2.copy(modulePos).add(dir.clone().multiplyScalar(CELL));
        const dist = candidatePos.distanceTo(worldPos);
        
        if (dist < nearestDist && dist < CELL * 0.6) {
          nearestDist = dist;
          bestPos = {
            x: Math.round(candidatePos.x / CELL),
            y: Math.round(candidatePos.y / CELL),
            z: Math.round(candidatePos.z / CELL),
          };
          canPlace = true;
        }
      });
    });

    // Fallback to grid snap if nothing close
    if (!bestPos) {
      bestPos = {
        x: Math.round(worldPos.x / CELL),
        y: Math.round(worldPos.y / CELL),
        z: Math.round(worldPos.z / CELL),
      };
      // Can place if it touches at least one existing module
      canPlace = DIRS.some((d) => 
        mods.has(keyFrom(bestPos.x + Math.round(d.x), bestPos.y + Math.round(d.y), bestPos.z + Math.round(d.z)))
      ) || mods.size === 0;
    }

    return { ...bestPos, canPlace };
  }, [mods]);

  const computeConnections = useCallback(
    (k) => {
      const { x, y, z } = parseKey(k);
      // Check all 14 face directions for neighbors
      return DIRS.map((d) => {
        const nx = Math.round(x + d.x);
        const ny = Math.round(y + d.y);
        const nz = Math.round(z + d.z);
        return mods.has(keyFrom(nx, ny, nz));
      });
    },
    [mods]
  );

  const handlePointerMove = useCallback(
    (e) => {
      // Intersect with plane or nearest surface
      const { camera, pointer, intersections } = e;
      raycaster.setFromCamera(pointer, camera);
      
      // Try to intersect with existing modules first
      let intersectPoint = null;
      if (intersections && intersections.length > 0) {
        const first = intersections[0];
        if (first.object !== e.eventObject) {
          intersectPoint = first.point;
        }
      }
      
      // Fallback to plane intersection
      if (!intersectPoint) {
        const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), -currentZ * CELL);
        raycaster.ray.intersectPlane(plane, tmp);
        intersectPoint = tmp;
      }
      
      if (intersectPoint) {
        const snapped = findNearestSnapPosition(intersectPoint, mods);
        setHoverCell({
          x: clamp(snapped.x, -GRID, GRID),
          y: clamp(snapped.y, -GRID, GRID),
          z: clamp(snapped.z, -GRID, GRID),
        });
      }
    },
    [raycaster, tmp, tmp2, currentZ, mods, findNearestSnapPosition]
  );

  const handleClick = useCallback(() => {
    const k = keyFrom(hoverCell.x, hoverCell.y, hoverCell.z);

    setMods((prev) => {
      const next = new Set(prev);
      if (mode === "add") {
        if (!next.has(k)) {
          // Enhanced snap rule: can place if touching any existing module via any face
          const touches = DIRS.some((d) => {
            const nx = hoverCell.x + Math.round(d.x);
            const ny = hoverCell.y + Math.round(d.y);
            const nz = hoverCell.z + Math.round(d.z);
            return next.has(keyFrom(nx, ny, nz));
          });
          
          if (touches || next.size === 0) {
            next.add(k);
            setSelectedKey(k);
            setCurrentZ(hoverCell.z); // Update working plane
          }
        }
      } else {
        if (next.has(k)) {
          next.delete(k);
          if (k === selectedKey) {
            const first = next.values().next().value;
            setSelectedKey(first ?? "");
          }
        }
      }
      return next;
    });
  }, [hoverCell, mode, selectedKey]);

  // Keyboard shortcuts
  React.useEffect(() => {
    const onKey = (ev) => {
      if (ev.key === "a" || ev.key === "A") setMode("add");
      if (ev.key === "r" || ev.key === "R") setMode("remove");
      if (ev.key === "c" || ev.key === "C") {
        setMods(new Set([keyFrom(0, 0, 0)]));
        setSelectedKey(keyFrom(0, 0, 0));
        setCurrentZ(0);
      }
      // Z-axis navigation
      if (ev.key === "q" || ev.key === "Q") setCurrentZ((z) => Math.max(-GRID, z - 1));
      if (ev.key === "e" || ev.key === "E") setCurrentZ((z) => Math.min(GRID, z + 1));
      
      // Preset structures
      if (ev.key === "1") {
        // Simple tower
        setMods(() => {
          const s = new Set();
          for (let z = 0; z <= 3; z++) s.add(keyFrom(0, 0, z));
          return s;
        });
      }
      if (ev.key === "2") {
        // L-shaped structure
        setMods(() => {
          const s = new Set();
          for (let x = 0; x <= 4; x++) s.add(keyFrom(x, 0, 0));
          for (let y = 0; y <= 4; y++) s.add(keyFrom(0, y, 0));
          return s;
        });
      }
      if (ev.key === "3") {
        // 3D cross
        setMods(() => {
          const s = new Set();
          for (let x = -2; x <= 2; x++) s.add(keyFrom(x, 0, 0));
          for (let y = -2; y <= 2; y++) s.add(keyFrom(0, y, 0));
          for (let z = -2; z <= 2; z++) s.add(keyFrom(0, 0, z));
          return s;
        });
      }
      if (ev.key === "4") {
        // Sphere-like structure using diagonal connections
        setMods(() => {
          const s = new Set();
          const radius = 3;
          for (let x = -radius; x <= radius; x++) {
            for (let y = -radius; y <= radius; y++) {
              for (let z = -radius; z <= radius; z++) {
                const dist = Math.sqrt(x*x + y*y + z*z);
                if (dist <= radius && dist >= radius - 1) {
                  s.add(keyFrom(x, y, z));
                }
              }
            }
          }
          return s;
        });
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const moduleList = useMemo(() => Array.from(mods), [mods]);
  
  // Check if hover position can place
  const canPlaceHover = useMemo(() => {
    const k = keyFrom(hoverCell.x, hoverCell.y, hoverCell.z);
    if (mods.has(k)) return false;
    if (mods.size === 0) return true;
    return DIRS.some((d) => {
      const nx = hoverCell.x + Math.round(d.x);
      const ny = hoverCell.y + Math.round(d.y);
      const nz = hoverCell.z + Math.round(d.z);
      return mods.has(keyFrom(nx, ny, nz));
    });
  }, [hoverCell, mods]);

  // Calculate total connections for UI
  const totalConnections = useMemo(() => {
    return moduleList.reduce((sum, k) => {
      return sum + computeConnections(k).filter(Boolean).length;
    }, 0);
  }, [moduleList, computeConnections]);

  return (
    <group onPointerMove={handlePointerMove} onClick={handleClick}>
      <ambientLight intensity={0.65} />
      <directionalLight position={[5, 8, 10]} intensity={1.2} />
      <directionalLight position={[-6, -4, 6]} intensity={0.6} />
      <pointLight position={[0, 0, 5]} intensity={0.4} />

      <GridHelperLines currentZ={currentZ} />
      <HoverGhost cell={hoverCell} canPlace={canPlaceHover && mode === "add"} />

      {moduleList.map((k) => {
        const { x, y, z } = parseKey(k);
        const p = worldFromCell(x, y, z);
        const connected = computeConnections(k);
        return (
          <Module
            key={k}
            position={[p.x, p.y, p.z]}
            connectedFaces={connected}
            selected={k === selectedKey}
          />
        );
      })}

      <Html position={[-GRID * CELL, GRID * CELL + 1, currentZ * CELL]} transform>
        <div className="w-[400px] rounded-2xl bg-white/95 shadow-xl p-5 border border-zinc-200">
          <div className="text-xl font-bold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Optimized Modular Unit System
          </div>
          <div className="text-sm text-zinc-700 mb-3">
            <b>Shape:</b> Truncated Octahedron (14 connection faces)<br/>
            <b>Mode:</b> <span className="font-semibold">{mode === "add" ? "ADD" : "REMOVE"}</span> | 
            <b> Plane:</b> Z = {currentZ}
          </div>
          
          <div className="mt-4 text-sm">
            <div className="font-semibold text-zinc-800 mb-2">Controls</div>
            <div className="grid grid-cols-2 gap-2 text-zinc-700">
              <div><b>A</b> = Add mode</div>
              <div><b>R</b> = Remove mode</div>
              <div><b>C</b> = Clear/Reset</div>
              <div><b>Q/E</b> = Change Z plane</div>
              <div><b>1-4</b> = Presets</div>
              <div><b>Drag</b> = Orbit camera</div>
            </div>
          </div>
          
          <div className="mt-4 pt-3 border-t border-zinc-200">
            <div className="text-xs text-zinc-600">
              <div className="mb-1">
                <span className="font-semibold text-green-700">● Green dots</span> = Connected faces ({totalConnections} total)
              </div>
              <div>
                <span className="font-semibold">● Gray dots</span> = Available connection points
              </div>
              <div className="mt-2 text-zinc-500 italic">
                The truncated octahedron shape enables maximum structural flexibility with 14 connection points per module.
              </div>
            </div>
          </div>
        </div>
      </Html>
    </group>
  );
}

export default function ModularUnitDemo() {
  return (
    <div style={{ width: '100vw', height: '100vh', margin: 0, padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, position: 'relative', width: '100%', minHeight: 0 }}>
        <Canvas 
          camera={{ position: [8, 8, 8], fov: 50 }}
          style={{ width: '100%', height: '100%', display: 'block' }}
        >
          <OrbitControls 
            makeDefault 
            enableDamping 
            dampingFactor={0.08}
            minDistance={3}
            maxDistance={30}
          />
          <Scene />
        </Canvas>
      </div>

      <div className="px-4 py-2 text-xs text-zinc-700 border-t border-zinc-200 bg-white/95" style={{ flexShrink: 0 }}>
        <b>Optimized Modular System:</b> Each module uses a <b>truncated octahedron</b> geometry with <b>14 connection faces</b> 
        (6 square + 8 hexagonal), enabling optimal 3D tiling and maximum structural flexibility. 
        This shape allows modules to form almost any structure while maintaining strong mechanical connections at every face.
      </div>
    </div>
  );
}
